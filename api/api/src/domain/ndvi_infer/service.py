import datetime
import json 
import uuid 
from fastapi.responses import StreamingResponse
from fastapi import APIRouter, Form, BackgroundTasks, HTTPException, Depends

from starlette.status import HTTP_200_OK, HTTP_400_BAD_REQUEST,HTTP_500_INTERNAL_SERVER_ERROR
from init_mq import redis, celery_execute

from src import config
from src.depenencies import * 
from src.domain.ndvi_infer.schemas import *

import asyncio



# print(redis, celery_execute)
async def sleep(delay=0.5):
    await asyncio.sleep(delay)

async def ndvi_inference(background_task):
    time = now_utc()
    task_id = str(uuid.uuid5(uuid.NAMESPACE_OID, config.ML_QUERY_NAME + "_" + str(time)))
    time_handle = MlTimeHandle(start_process=str(time.timestamp())).__dict__
    status_handle = MlStatusHandle().__dict__
    data = MlResult(task_id=task_id, time=time_handle, status=status_handle)
    redis.set(task_id, json.dumps(data.__dict__))
    background_task.add_task(product_ndvi_infer_background, task_id, time, data)
    return MlResponse(status="PENDING", time=time, status_code=HTTP_200_OK, task_id=task_id)

async def ndvi_preprocess(background_task):
    time = now_utc()
    task_id = str(uuid.uuid5(uuid.NAMESPACE_OID, config.ML_QUERY_NAME + "_" + str(time)))
    time_handle = MlTimeHandle(start_process=str(time.timestamp())).__dict__
    status_handle = MlStatusHandle().__dict__
    data = MlResult(task_id=task_id, time=time_handle, status=status_handle)
    redis.set(task_id, json.dumps(data.__dict__))
    background_task.add_task(product_ndvi_process_background, task_id, time, data)
    return MlResponse(status="PENDING", time=time, status_code=HTTP_200_OK, task_id=task_id)

def product_ndvi_process_background(task_id: str, time: datetime, data: MlResult):
    try: 
        data.time['start_process'] = str(time.timestamp())
        data_dump = json.dumps(data.__dict__)
        redis.set(task_id, data_dump)
        print('start celery task')
        celery_execute.send_task(
            name=config.ML_QUERY_NAME + "." + config.PREPARE_TASK_NAME,
            kwargs={
                "task_id": task_id,
                "sync": False
            },
            queue = config.ML_QUERY_NAME
        )
        print('end celery task')
    except Exception as e:
        data.status['general_status'] = "FAILED"
        data.status['process_status'] = "FAILED"
        data.error = str(e)
        redis.set(task_id, json.dumps(data.__dict__))

def product_ndvi_infer_background(task_id: str, time: datetime, data: MlResult):
    try:
        data.time['start_process'] = str(time.timestamp())
        data_dump = json.dumps(data.__dict__)
        redis.set(task_id, data_dump)
        print('start celery task')
        celery_execute.send_task(
            name=config.ML_QUERY_NAME + "." + config.INFERENCE_TASK_NAME,
            kwargs={
                "task_id": task_id,
                "sync": False
            },
            queue = config.ML_QUERY_NAME
        )
        print('end celery task')
    except Exception as e:
        data.status['general_status'] = "FAILED"
        data.status['process_status'] = "FAILED"
        data.error = str(e)
        redis.set(task_id, json.dumps(data.__dict__))

def get_status(task_id: str) -> MlResult:
    data = redis.get(task_id)
    if data is None:
        raise HTTPException(status_code=400, detail="Task not found")
    message = json.loads(data)

    return MlResult(**message)