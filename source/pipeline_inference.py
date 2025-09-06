from download_image_from_minio.pipeline_download import pipeline_download
from prepare_data_services.preprocess_for_Test import create_json_data
from inference.model_inference import model_inference_NDVI
from logger.Logger import app_logger as logging

def pipeline_inference(input_params):
    try:
        logging.info("Starting pipeline inference")
        
        # Step 1: Download images
        image_path = pipeline_download(input_params)
        logging.info(f"Images downloaded to {image_path}")
        
        # Step 2: Prepare data
        create_json_data()
        logging.info("Data preparation completed")
        
        # Step 3: Model inference
        model_inference_NDVI(image_path)
        logging.info("Model inference completed successfully")
        
    except Exception as e:
        logging.error(f"Pipeline inference failed: {str(e)}")
        raise e

