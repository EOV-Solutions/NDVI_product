from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class ErrorInfo(BaseModel):
    code: Optional[str] = Field(None, description="Mã lỗi (VD: DOWNLOAD_ERROR)")
    detail: Optional[str] = Field(None, description="Chi tiết lỗi")


class TaskParams(BaseModel):
    bbox: Optional[list] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class TaskMetadata(BaseModel):
    params: Optional[TaskParams] = None
    output: Optional[str] = Field(None, description="Link output (VD: MinIO, DB, file)")


class TaskStatus(BaseModel):
    task_id: str = Field(..., description="UUID duy nhất của task")
    task_name: Optional[str] = Field(None, description="Tên job / pipeline")
    status: str = Field(
        ...,
        description="Trạng thái hiện tại",
        example="PENDING"
    )
    progress: float = Field(0.0, description="Tiến độ (%) 0.0 → 100.0")
    message: Optional[str] = Field(None, description="Thông báo chi tiết")
    
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None

    error: Optional[ErrorInfo] = None
    metadata: Optional[TaskMetadata] = None