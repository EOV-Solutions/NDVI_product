from __future__ import annotations
from abc import ABC, abstractmethod
import time

class DownloadImageFromMinioError(Exception):
    """Custom exception for errors during image download from MinIO."""
    pass

class InputParamsDownload:
    def __init__(self, bbox, start_date, end_date, task_id):
        self.bbox = bbox
        self.start_date = start_date
        self.end_date = end_date
        self.id = task_id
        self.status = "initialized"
        self.created_at = time.time()
        self.save_dir = f'/tmp/{task_id}'

class DownloadImage(ABC):
    @abstractmethod
    def download_image(self, input_params: InputParamsDownload) -> None:
        
        """Download image based on input parameters.
        
        Args:
            input_params (InputParamsDownload): Parameters for downloading the image.
        
        Raises:
            DownloadImageFromMinioError: If there is an error during the download process.
        """
        pass    