from source.processing_raw_image.processing_abstract import ProcessingImage
# from source.processing_raw_image.process_sentinel1 import ProcessSentinel1
from source.processing_raw_image.process_sentinel2 import ProcessSentinel2
ps1 = ProcessSentinel2('/mnt/storage/code/EOV_NDVI/BRIOS_v1-main/data/abc', 'abc')
ps1.processing_all_image()