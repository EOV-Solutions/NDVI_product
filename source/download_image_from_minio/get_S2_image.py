from download_image import DownloadImage, InputParamsDownload, DownloadImageFromMinioError
import os
from logger.Logger import app_logger as logging
import requests 


class DownloadS2ImageFromMinio(DownloadImage):
    def download_image(self, input_params: InputParamsDownload) -> None:
        try:
            # Ví dụ: query STAC API cho Sentinel-2
            url = "https://example-stac-api.com/collections/sentinel-2/items"
            query = {
                "datetime": f"{input_params.start_date}/{input_params.end_date}",
                "intersects": input_params.geojson_file,
            }
            resp = requests.post(url, json=query, timeout=30)
            resp.raise_for_status()

            data = resp.json()
            # xử lý dữ liệu (chỉ minh họa)
            print(f"[Sentinel-1] {len(data.get('features', []))} items found.")

            input_params.status = "SUCCESS"
            return "path to file"
        except Exception as e:
            input_params.status = "FAILED"
            raise DownloadImageFromMinioError(
                f"Error downloading Sentinel-1 image: {str(e)}"
            )