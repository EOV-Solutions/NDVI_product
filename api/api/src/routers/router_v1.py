from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from ..domain.ndvi_infer.schemas import MlResult
from ..domain.ndvi_infer import service
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)


@router.post("/ndvi_infer/preprocess")
async def preprocess(background_tasks: BackgroundTasks):
    return await service.ndvi_preprocess(background_tasks)

@router.post("/ndvi_infer/inference")
async def inference(background_tasks: BackgroundTasks):
    return await service.ndvi_inference(background_tasks)

@router.get("/status/{task_id}", response_model=MlResult)
def status(task_id: str,):
    return service.get_status(task_id)

