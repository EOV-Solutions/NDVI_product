import os
import sys
__dir__ = os.path.dirname(os.path.abspath(__file__))
sys.path.append(__dir__)
sys.path.insert(0, os.path.abspath(os.path.join(__dir__, '../')))

from celery import Celery, Task
from init_broker import is_broker_running
from init_redis import is_backend_running

from celery_worker.init_mq import redis
from celery_worker.helpers import time as time_helper
from celery_worker.settings import celery_config, config
from celery_worker.helpers.storage import create_path

from download_image_from_minio.download_image import InputParamsDownload
from download_image_from_minio.pipeline_download import pipeline_download
from processing_raw_image.pipeline_process import processing_image
from prepare_data_services.preprocess_for_Test import create_json_data
from inference.model_inference import model_inference_NDVI

from logger.Logger import app_logger as logging
if not is_backend_running(): exit()
if not is_broker_running(): exit()


app = Celery(celery_config.QUERY_NAME, broker=config.BROKER, backend=config.REDIS_BACKEND)
app.config_from_object('settings.celery_config')

@app.task(bind=True, name="{query}.{task_name}".format(query=celery_config.QUERY_NAME, task_name=celery_config.FULL_PROCESS_INFERENCE))
def full_process_task(self, task_id: str, sync: bool, input: InputParamsDownload):
    # Step 1: Downloading data from ROI
    logging.info(f"Starting download image")
    pipeline_download(input)

    # Step 2: Processing raw image 
    logging.info("Starting processing raw image")
    processing_image(input)

    # Step 3: Prepare data for Inference
    logging.info(f"Starting prepare data task {task_id} ")
    create_json_data(input.root_dir, input.id)
    
    # Step 4: Inference 
    logging.info("Starting inference NDVI !!!!")
    model_inference_NDVI(os.path.join(input.root_dir, 'processed'))



    redis.set(task_id, "running")


