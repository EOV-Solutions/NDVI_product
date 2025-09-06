import datetime
import pytz 
from typing import List
from starlette.config import Config
from starlette.datastructures import CommaSeparatedStrings, Secret


#=========================================================================
#                           TIMING CONFIG
#=========================================================================
u = datetime.datetime.utcnow()
u = u.replace(tzinfo=pytz.timezone("Asia/Ho_Chi_Minh"))


#=========================================================================
#                          PROJECT INFORMATION 
#=========================================================================
# Properties configurations

API_PREFIX = "/api"
JWT_TOKEN_PREFIX = "Authorization"
# config = Config(".env")
ROUTE_PREFIX_V1 = "/v1"
# ALLOWED_HOSTS: List[str] = config(
#     "ALLOWED_HOSTS",
#     cast=CommaSeparatedStrings,
#     default="",
# )

PROJECT_NAME = 'NDVI Inference Service'
HOST = '0.0.0.0'
PORT = 8082
# USER = PROJECT['user']
# PASSWORD = PROJECT['password']

#=========================================================================
#                          REDIS INFORMATION 
#=========================================================================
REDIS_HOST = 'redis-sentinel.eovdc.svc.cluster.local'
REDIS_PORT = 6379
REDIS_PASSWORD = 'eovdc@2025$%'
REDIS_DB = 1
REDIS_BACKEND = "redis://:{password}@{hostname}:{port}/{db}".format(
    hostname=REDIS_HOST,
    password=REDIS_PASSWORD,
    port=REDIS_PORT,
    db=REDIS_DB
)


#=========================================================================
#                          BROKER INFORMATION 
#=========================================================================
BROKER = "amqp://{user}:{pw}@{hostname}:{port}/{vhost}".format(
    user='admin',
    pw='rabbitmq123456',
    hostname='eov-rabbitmq-service.eovdc.svc.cluster.local',
    port=5672,
    vhost=''
)


# #=========================================================================
# #                          ML INFORMATION 
# #=========================================================================
PREPARE_TASK_NAME = 'prepare_task'
INFERENCE_TASK_NAME = 'inference_task'
ML_QUERY_NAME = 'ndvi_inference_celery'