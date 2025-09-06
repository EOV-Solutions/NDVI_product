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

from prepare_data_services.preprocess_for_Test import create_json_data
from inference.model_inference import model_inference_NDVI
from logger.Logger import app_logger as logging
if not is_backend_running(): exit()
if not is_broker_running(): exit()


app = Celery(celery_config.QUERY_NAME, broker=config.BROKER, backend=config.REDIS_BACKEND)
app.config_from_object('settings.celery_config')

@app.task(bind=True, name="{query}.{task_name}".format(query=celery_config.QUERY_NAME, task_name=celery_config.PREPARE_TASK_NAME))
def prepare_data_task(self, task_id: str, sync: bool):
    logging.info(f"Starting prepare data task {task_id} ")
    create_json_data()
    logging.info("Ending prepare data task")
    redis.set(task_id, "running")

@app.task(bind=True, name="{query}.{task_name}".format(query=celery_config.QUERY_NAME, task_name=celery_config.INFERENCE_TASK_NAME))
def inference_task(self, task_id: str, sync: bool):
    """
    Task to perform inference on the prepared data.
    """
    try:
        logging.info(f"Starting inference task {task_id}")
        dir = '/app/data'
        model_path = '/app/inference/model_file/brios_base_FINAL_extreme.pt'
        minio = 'ndvi-infer'
        model_inference_NDVI(dir, model_path, minio)
        redis.set(task_id, "completed")
        logging.info(f"Inference task {task_id} completed successfully")
    except Exception as e:
        redis.set(task_id, "failed")
        logging.error(f"Inference task {task_id} failed: {str(e)}")
        raise e