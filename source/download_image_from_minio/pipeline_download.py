from download_image_from_minio.get_S1_image import DownloadS1ImageFromMinio
from download_image_from_minio.get_S2_image import DownloadS2ImageFromMinio

def pipeline_download(input_params):
    try:
        downloader_s1 = DownloadS1ImageFromMinio()
        downloader_s1.download_image(input_params)
        
        downloader_s2 = DownloadS2ImageFromMinio()
        downloader_s2.download_image(input_params)
        
        return input_params.status
    except Exception as e:
        return f"Pipeline download failed: {str(e)}"