from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, UploadFile, File
from ..domain.ndvi_infer.schemas import MlResult
from ..domain.ndvi_infer import service
from pydantic import BaseModel
router = APIRouter(
    dependencies=[],
    responses={404: {"description": "Not found"}},
)

class InferenceRequest(BaseModel):
    bbox: List[float]  
    start_date: str   
    end_date: str      

@router.post("/ndvi_infer/full_process_inference")
async def full_process_inference(request: InferenceRequest, background_tasks: BackgroundTasks):
    return await service.full_process_inference(
        bbox=request.bbox,
        start_date=request.start_date,
        end_date=request.end_date,
        background_tasks=background_tasks
    )


@router.get("/status/{task_id}", response_model=MlResult)
def status(task_id: str,):
    return service.get_status(task_id)

