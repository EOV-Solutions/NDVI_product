from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
import uuid
import time

class DownloadImageFromMinioError(Exception):
    """Custom exception for errors during image download from MinIO."""
    pass

class InputParamsDownload:
    def __init__(self, geojson_file, start_date, end_date):
        self.geojson_file = geojson_file
        self.start_date = start_date
        self.end_date = end_date
        self.id = str(uuid.uuid4()) 
        self.status = "initialized"
        self.created_at = time.time()

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