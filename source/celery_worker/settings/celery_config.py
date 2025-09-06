from kombu import Queue
import configparser


cfg = configparser.ConfigParser()
cfg.read('./env.ini')

#=========================================================================
#                          CELERY INFORMATION 
#=========================================================================
CELERY = cfg['celery']

# Set worker to ack only when return or failing (unhandled expection)
task_acks_late = True

# Worker only gets one task at a time
worker_prefetch_multiplier = 1

QUERY_NAME = CELERY["query"]

# Create queue for worker
task_queues = [Queue(name=QUERY_NAME)]

# Set Redis key TTL (Time to live)
result_expires = 60 * 60 * 48  # 48 hours in seconds


# #=========================================================================
# #                          ML INFORMATION 
# #=========================================================================
PREPARE_TASK_NAME = CELERY['prepare_task_name']
INFERENCE_TASK_NAME = CELERY['inference_task_name']