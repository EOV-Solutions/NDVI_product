import torch
import numpy as np
from math import sqrt
from sklearn import metrics
import utils as utils
import inference.models as models
from inference.dataloader import batch_data_loader
from tqdm import tqdm
import os
import re
import rasterio
from logger.Logger import app_logger as logging
from minio.minio_utils import get_minio_s3_client, ensure_minio_bucket_exists, upload_bytes_to_minio
import io
import shutil
import boto3
from botocore.config import Config


# parameters
model_name = 'brios'
hid_size = 96
SEQ_LEN = 46
INPUT_SIZE = 3
SELECT_SIZE = 1
X, Y = 0, 15
SavePath =  '/inference/model_file/brios_base_FINAL_extreme.pt' 



def load_model(model_path):
    model = getattr(models, model_name).Model(hid_size, INPUT_SIZE, SEQ_LEN, SELECT_SIZE)
    model.load_state_dict(torch.load(model_path))
    model.eval()  # Set model to evaluation mode
    if torch.cuda.is_available():
        model = model.cuda()
    return model

def upload_file_infer(bucket_name, prefix, local_dir):
        """
        Upload a JSON file to MinIO.

        Parameters:
            bucket_name (str): Name of the MinIO bucket.
            prefix (str): Prefix (folder path) in the bucket where the file will be uploaded.
            local_dir (str): Local directory containing the JSON file to upload.
        """
        s3 = boto3.client(
            's3',
            endpoint_url='http://minio:9000',
            aws_access_key_id='ROOTNAME',
            aws_secret_access_key='CHANGEME123',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1'
        )
        json_file_path = os.path.join(local_dir, 'data_infer.json')

        if not os.path.exists(json_file_path):
            logging.error(f"File {json_file_path} does not exist.")
            return

        minio_path = os.path.join(prefix, 'data_infer.json')

        try:
            with open(json_file_path, 'rb') as file_data:
                s3.put_object(
                    Bucket=bucket_name,
                    Key=minio_path,
                    Body=file_data,
                    ContentType='application/json'
                )
            logging.info(f"Uploaded {json_file_path} to MinIO bucket {bucket_name} at {minio_path}")
        except Exception as e:
            logging.error(f"Failed to upload {json_file_path} to MinIO: {e}")

def inference(DIR, model_path):
    data_path = os.path.join(DIR, 'data_infer.json')
    data_iter = batch_data_loader.get_test_loader(batch_size=1024, prepath=data_path)
    logging.info(f"Data loader created with {data_iter}")
    # logging.info('111111111111')
    model = load_model(model_path)
    # logging.info('222222222222')
    all_predictions = [] 
    # logging.info('2,555555555555555')
  
    with torch.no_grad(): 
        # try:
        # logging.info('2,666666666666666') 
        for idx, data in enumerate(data_iter):
            logging.info(f"Processing batch {idx+1}")
            data = utils.to_var(data)

            ret = model.run_on_batch(data, None)

            predictions = ret['imputations'].data.cpu().numpy()
            logging.info(f"[{idx}] Predictions shape: {predictions.shape}")

            if np.any(predictions == -100) or np.any(np.isnan(predictions)):
                logging.warning(f"Warning: -100 or NaN values found in predictions for iteration {idx}")
            all_predictions.append(predictions)
        # except Exception as e:
        #     logging.exception("Unhandled exception during inference")
            
    # logging.info('333333333333')
    all_predictions = np.concatenate(all_predictions, axis=0)
    np.save(os.path.join(DIR, 'infer.npy'), all_predictions)
    logging.info(f"Predictions saved for region")

def model_npy_to_tiff(dir, minio_bucket_name=''):
    """
    Processes infer.npy and ndvi_timeseries.npy, combines them (if ground truth exists),
    and uploads the resulting TIFF files directly to MinIO S3 using minio_utils.

    Args:
        dir (str): The base directory containing region folders.
        minio_bucket_name (str): The name of the MinIO bucket to upload to.
    """
    # Ensure the target bucket exists using your utility function
    try:
        ensure_minio_bucket_exists(minio_bucket_name)
    except Exception as e:
        logging.critical(f"Failed to ensure MinIO bucket '{minio_bucket_name}' exists. Aborting: {e}")
        return



    npy_path = os.path.join(dir, 'infer.npy')
    if not os.path.exists(npy_path):
        logging.warning(f"infer.npy not found at {npy_path}. Skipping.")
        return

    # logging.info(f"Loading predictions from {npy_path}")
    imputation_array = np.load(npy_path)

    # Load ground truth NDVI data
    gt_npy_path = os.path.join(dir, 'ndvi_timeseries.npy')
    gt_array = None
    if os.path.exists(gt_npy_path):
        # logging.info(f"Loading ground truth from {gt_npy_path}")
        gt_array = np.load(gt_npy_path)
        if gt_array.shape != imputation_array.shape:
            logging.warning(f"Shape mismatch between imputation {imputation_array.shape} and GT {gt_array.shape}. Ground truth will be ignored.")
            gt_array = None
    else:
        logging.warning(f"Ground truth file not found at {gt_npy_path}. Using imputation only.")

    # Check for NaNs in the entire NDVI inference array
    if np.isnan(imputation_array).any():
        logging.warning(f"NaN values found in NDVI inference for region")

    # Identify RVI and NDVI subfolders
    rvi_folder = None
    ndvi_folder = None
    for sub in os.listdir(dir):
        sub_path = os.path.join(dir, sub)
        if os.path.isdir(sub_path):
            low = sub.lower()
            if 'rvi' in low:
                rvi_folder = sub_path
            if 'ndvi8days' in low:
                ndvi_folder = sub_path

    if not rvi_folder or not ndvi_folder:
        logging.warning(f"Missing RVI or NDVI folder for region. Skipping.")
        return

    # Extract dates from RVI TIFF filenames
    tif_files = [f for f in os.listdir(rvi_folder) if f.endswith('.tif')]
    dates = []
    for tif_file in tqdm(tif_files, desc=f"Extracting dates"):
        m = re.search(r'(\d{4}-\d{2}-\d{2})', tif_file)
        if m:
            dates.append(m.group(1))
    dates.sort()

    # Validate time steps
    num_timesteps = imputation_array.shape[1]

    # Read metadata from a sample NDVI file
    sample_tifs = [f for f in os.listdir(ndvi_folder) if f.endswith('.tif')]
  
    sample_path = os.path.join(ndvi_folder, sample_tifs[0])
    with rasterio.open(sample_path) as src:
        meta = src.meta.copy()

    # Update metadata for output TIFF
    meta.update(count=1, dtype=rasterio.float32, nodata=-100.0)

    height, width = meta['height'], meta['width']
    logging.info(f"Processing {num_timesteps} time slices for region")
    for idx, date in enumerate(tqdm(dates, desc=f"Uploading NDVI TIFFs")):
        imputation_slice = imputation_array[:, idx, 0].reshape((height, width))
        
        final_slice = imputation_slice

        if gt_array is not None:
            gt_slice = gt_array[:, idx, 0].reshape((height, width))
            # Create a combined slice: use GT where it's valid, otherwise use imputation
            final_slice = np.where(gt_slice != -100, gt_slice, imputation_slice)

        # Check for NaNs in each slice
        if np.isnan(final_slice).any():
            logging.warning(f"NaN values in NDVI slice for date {date}")

        # Define the object name in MinIO (path within the bucket)
        object_name = f"ndvi_infer_8days/ndvi8days_infer_{date}.tif"

        # Use an in-memory byte stream to write the TIFF
        buffer = io.BytesIO()
        with rasterio.open(buffer, 'w', **meta) as dst:
            dst.write(final_slice.astype(np.float32), 1)
        
        buffer.seek(0) # Rewind the buffer to the beginning


        # TODO: Sau này có thể sửa thành upload MINIO theo chuẩn STAC và thực hiện đăng ký STAC API 
        # Upload bytes to MinIO using the utility function
        # success = upload_bytes_to_minio(
        #     data_bytes=buffer.getvalue(), # Get the bytes content from the buffer
        #     bucket_name=minio_bucket_name,
        #     object_name=object_name,
        #     content_type="image/tiff"
        # )
        # if not success:
        #     logging.error(f"Failed to upload {object_name}. See previous logs for details.")


        
def model_inference_NDVI(DIR, model_path, minio_bucket_name):
    inference(DIR, model_path)
    # logging.info('44444444444')
    model_npy_to_tiff(DIR, minio_bucket_name)
    if os.path.exists(DIR) and os.path.isdir(DIR):
        try:
            shutil.rmtree(DIR)
            logging.info(f"Successfully cleaned up directory: {DIR}")
        except OSError as e:
            logging.error(f"Error cleaning up directory {DIR}: {e}", exc_info=True)
            logging.warning("Please check permissions or if the directory is in use.")
    else:
        logging.info(f"Directory {DIR} does not exist or is not a directory. No cleanup needed.")
