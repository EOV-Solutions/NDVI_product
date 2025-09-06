# src/utils/minio_utils.py

import boto3
from botocore.exceptions import ClientError
import logging
import os
from dotenv import load_dotenv
from io import BytesIO
load_dotenv()

MINIO_ENDPOINT_URL = 'http://minio:9000/'
MINIO_ACCESS_KEY = 'ROOTNAME'
MINIO_SECRET_KEY = 'CHANGEME123'
MINIO_SECURE = False  # Set to True if your MinIO uses HTTPS

s3_client = None

def get_minio_s3_client():
    global s3_client
    if s3_client is None:
        try:
            s3_client = boto3.client(
                's3',
                endpoint_url=MINIO_ENDPOINT_URL,
                aws_access_key_id=MINIO_ACCESS_KEY,
                aws_secret_access_key=MINIO_SECRET_KEY,
                use_ssl=MINIO_SECURE,
                verify=MINIO_SECURE
            )
            logging.info("MinIO S3 client initialized.")
        except Exception as e:
            logging.error(f"Failed to initialize MinIO S3 client: {e}")
            raise
    return s3_client

def ensure_minio_bucket_exists(bucket_name):
    client = get_minio_s3_client()
    try:
        client.head_bucket(Bucket=bucket_name)
        logging.info(f"MinIO bucket '{bucket_name}' already exists.")
    except ClientError as e:
        error_code = int(e.response['Error']['Code'])
        if error_code == 404:
            logging.info(f"MinIO bucket '{bucket_name}' does not exist. Creating...")
            try:
                client.create_bucket(Bucket=bucket_name)
                logging.info(f"MinIO bucket '{bucket_name}' created successfully.")
            except ClientError as create_e:
                logging.error(f"Failed to create MinIO bucket '{bucket_name}': {create_e}")
                raise
        else:
            logging.error(f"Error checking MinIO bucket '{bucket_name}': {e}")
            raise

def upload_bytes_to_minio(data_bytes, bucket_name, object_name, content_type='application/octet-stream'):
    client = get_minio_s3_client()
    try:
        logging.info(f"Uploading {object_name} to MinIO bucket '{bucket_name}'...")
        client.put_object(
            Bucket=bucket_name,
            Key=object_name,
            Body=data_bytes,
            ContentType=content_type
        )
        logging.info(f"Successfully uploaded {object_name} to MinIO.")
        return True
    except ClientError as e:
        logging.error(f"Failed to upload {object_name} to MinIO: {e}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred while uploading to MinIO: {e}")
        return False


def upload_file_to_minio(file_path, bucket_name, object_name=None, content_type='application/octet-stream'):
    if object_name is None:
        object_name = os.path.basename(file_path)

    client = get_minio_s3_client()
    try:
        logging.info(f"Uploading file {file_path} to {bucket_name}/{object_name}...")
        client.upload_file(file_path, bucket_name, object_name)
        logging.info(f"Successfully uploaded {object_name} from file.")
        return True
    except ClientError as e:
        logging.error(f"Failed to upload file {object_name}: {e}")
        return False
    except FileNotFoundError:
        logging.error(f"Error: File not found at {file_path}")
        return False
    except Exception as e:
        logging.error(f"An unexpected error occurred during file upload: {e}")
        return False
    
def get_bucket(bucket_name, prefix):
    client = get_minio_s3_client()
    byte_buffers = []  # List to hold byte data of images
    try:
        logging.info(f"Retrieving bucket {bucket_name}...")
        response = client.list_objects_v2(Bucket=bucket_name, Prefix=prefix)
        contents = response.get("Contents", [])
        for obj in contents:
            key = obj["Key"]
            if key.lower().endswith(".tif"):
                print(f"⬇️ Đang tải ảnh từ MinIO: {key}")
                s3_response = s3_client.get_object(Bucket=bucket_name, Key=key)
                byte_data = BytesIO(s3_response["Body"].read())  # đọc vào RAM
                byte_buffers.append(byte_data)  # giữ lại để xử lý sau
        if 'Contents' in response:
            logging.info(f"Bucket {bucket_name} contains {len(response['Contents'])} objects.")
            return byte_buffers, key
        else:
            logging.info(f"Bucket {bucket_name} is empty or does not exist.")
            return []
    except ClientError as e:
        logging.error(f"Failed to retrieve bucket {bucket_name}: {e}")
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred while retrieving bucket: {e}")
        return None
