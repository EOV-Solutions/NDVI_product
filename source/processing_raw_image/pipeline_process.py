from processing_raw_image.process_sentinel1 import ProcessSentinel1
from processing_raw_image.process_sentinel2 import ProcessSentinel2
from download_image_from_minio.download_image import InputParamsDownload


def processing_image(input_params: InputParamsDownload):
    process_s1 = ProcessSentinel1(input_params.root_dir, input_params.id)
    process_s1.processing_all_image()
    
    process_s2 = ProcessSentinel2(input_params.root_dir, input_params.id)
    process_s2.processing_all_image()