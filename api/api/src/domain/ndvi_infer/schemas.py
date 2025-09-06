from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MlTimeHandle(BaseModel):
    start_process: str = None
    end_process: str = None

class MlStatusHandle(BaseModel):
    general_status: str = "PENDING"
    process_status: str = None

class MlResult(BaseModel):
    task_id: str
    status: dict = None
    time: dict = None
    process_result: dict = None
    error: Optional[str] = None

class MlResponse(BaseModel):
    status: str
    status_code: int
    time: datetime
    task_id: str
 