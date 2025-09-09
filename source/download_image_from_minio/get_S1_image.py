from download_image import DownloadImage, InputParamsDownload, DownloadImageFromMinioError
import os
import zipfile
from source.logger.Logger import app_logger as logging
import requests 
from datetime import datetime 

### DEFINED SENTINEL 1 ###
BANDS = ["vv", "vh"] 
HOST = 'http://10.0.1.79:8000/' #TODO: Sau clean lai dua vao config

class DownloadS1ImageFromMinio(DownloadImage):
      def download_image(self, input_params: InputParamsDownload) -> None:
        try:
            # Ví dụ: query STAC API cho Sentinel-1
            api_search = f"{HOST}/v1/s1_search"
            query = {
                "bbox": input_params.bbox,
                "datetime": f"{input_params.start_date}/{input_params.end_date}",
                "bands": BANDS,                     
            }
            logging.info('start search')
            response = requests.post(api_search, json=query, timeout=30)
            response.raise_for_status()

            data = response.json()

            # DOWNLOAD 
            api_download = f"{HOST}/v1/s1_download/{data["task_id"]}"
            save_dir = f"{input_params.save_dir}/sentinel1"
            os.makedirs(save_dir, exist_ok=True)

            zip_path = os.path.join(save_dir, f"{input_params.id}.zip")
            logging.info("start download")
            response_download = requests.get(api_download, stream=True)
            response_download.raise_for_status()

            with open(zip_path, "wb") as f:
                for chunk in response_download.iter_content(chunk_size=8192):
                    f.write(chunk)

    
            logging.info("Download sentinel 1 Succesfully!!!!")

            logging.info("start unzip")
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(save_dir)
            logging.info("Unzip completed!")

            if os.path.exists(zip_path):
                os.remove(zip_path)
                logging.info(f"Removed zip file: {zip_path}")

            input_params.status = "SUCCESS"
            return save_dir
        
        except Exception as e:
            input_params.status = "FAILED"
            raise DownloadImageFromMinioError(
                f"Error downloading Sentinel-1 image: {str(e)}"
            )
        
        
if __name__ == "__main__":
    product_id = "20220504T223726_20220504T223754_043067_052498"

    # Cắt chuỗi start và end
    start_str, end_str = product_id.split("_")[0:2]
    start_dt = datetime.strptime(start_str, "%Y%m%dT%H%M%S")
    end_dt = datetime.strptime(end_str, "%Y%m%dT%H%M%S")
    
    # Đưa về dạng ISO 8601 với Z (UTC)
    start_iso = start_dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_iso = end_dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    input_params = InputParamsDownload(
        bbox=[106.5878, 9.6198, 107.0451, 10.6885],
        start_date=start_iso,
        end_date=end_iso,
        task_id='abc'
    )

    downloader_s1 = DownloadS1ImageFromMinio()
    logging.info(downloader_s1)
    a = downloader_s1.download_image(input_params)
    logging.info(a)