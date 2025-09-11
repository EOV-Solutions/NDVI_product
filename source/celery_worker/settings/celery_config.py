from kombu import Queue
import configparser
from dotenv import load_dotenv
import os 
# Load .env
load_dotenv(".env")

# cfg = configparser.ConfigParser()
# cfg.read('./env.ini')

#=========================================================================
#                          CELERY INFORMATION 
#=========================================================================
# CELERY = cfg['celery']

# Set worker to ack only when return or failing (unhandled expection)
task_acks_late = True

# Worker only gets one task at a time
worker_prefetch_multiplier = 1

QUERY_NAME = os.getenv("CELERY_QUERY", "ndvi_inference_celery")

# Create queue for worker
task_queues = [Queue(name=QUERY_NAME)]

# Set Redis key TTL (Time to live)
result_expires = 60 * 60 * 48  # 48 hours in seconds


# #=========================================================================
# #                          ML INFORMATION 
# #=========================================================================
FULL_PROCESS_INFERENCE = os.getenv("CELERY_FULL_PROCESS_TASK", "full_process_task")
TEST = os.getenv("CELERY_TEST_TASK","test")

print(QUERY_NAME, FULL_PROCESS_INFERENCE, TEST)