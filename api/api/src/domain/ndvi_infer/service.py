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



async def full_process_inference(bbox, start_date, end_date, background_tasks):
    time = now_utc()
    task_id = str(uuid.uuid5(uuid.NAMESPACE_OID, config.ML_QUERY_NAME + "_" + str(time)))

    input_params = {
        "bbox": bbox, 
        "start_date": start_date,
        "end_date": end_date
    }

    task_params = TaskParams(bbox=bbox, start_date=start_date, end_date=end_date)
    metadata = TaskMetadata(task_params=task_params, output=None)
    task_status = TaskStatus(
        task_id=task_id,
        task_name="inference",
        status="PENDING",
        progress=0.0,
        metadata=metadata
    )
    redis.set(task_id, json.dumps(task_status.dict(), default=str))
    # background_tasks.add_task(product_ndvi_full_process_background, task_id, time, data, input_params)
    product_ndvi_full_process_background(task_id, task_status, input_params)
    return task_status


##### ------------- PRODUCT Background Task Define ---------------------#####
def product_ndvi_full_process_background(task_id: str, task_status: TaskStatus, input_params: dict):
    try: 
        print('start celery task')
        
        print(config.ML_QUERY_NAME, " ", config.FULL_PROCESS_TASK_NAME)
        celery_execute.send_task(
            name=config.ML_QUERY_NAME + "." + config.FULL_PROCESS_TASK_NAME,
            kwargs={
                "task_id": task_id,
                "input_params": input_params,
                "task_status": task_status.dict()
            },
            queue = config.ML_QUERY_NAME
        )
        print('end celery task')
    except Exception as e:
        print(e)
        task_status.error = str(e)
        redis.set(task_id, json.dumps(task_status.dict(), default=str))



def get_status(task_id: str)->TaskStatus:
    data = redis.get(task_id)
    if data is None:
        raise HTTPException(status_code=404, detail="Task not found")

    raw = data.decode("utf-8").strip()
    print(f"[DEBUG] Redis raw data for {task_id} = {repr(raw)}")

    return TaskStatus.parse_raw(raw)