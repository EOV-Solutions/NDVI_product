import rasterio
from datetime import datetime
import os 
from processing_raw_image.processing_abstract import ProcessingImage
import numpy as np
from logger.Logger import app_logger as logging
""" 
    NOTE: Sentinel 3 file co 3 bands B04, B08, Omnicloudmask: format ten nhu sau <MA TEN>_<StartDate>_<EndDate>_<>_<>_<tenband>.tif 
        Truy xuat: B04: <Maten>_*_B04.tif, B08: <Maten>_*_B08.tif, CLM:  <Maten>_*_omnicloudmask.tif
"""
class ProcessSentinel2(ProcessingImage):
    def __init__(self, path_to_folder, task_id):
        super().__init__(path_to_folder, task_id)
        self.path_to_sentinel1_folder = os.path.join(self.path_to_folder, "raw/sentinel2")
        self.path_to_save_ndvi_image = os.path.join(self.path_to_folder, f"processed/{self.task_id}_ndvi8days")

    def calc_NDVI(self, b4_arr, b8_arr):
        ndvi_arr = (b8_arr - b4_arr) / (b8_arr + b4_arr + 1e-5)
        return ndvi_arr

    def cloud_mask(self, ndvi_arr, cls_arr):
        mask_image = np.where(cls_arr == 0, ndvi_arr, -100)
        logging.info(f"num mask {np.sum(cls_arr == 0)}")
        return mask_image


    def processing_single_image(self, b4_arr, b8_arr, cls_arr, metadata):
        # stack rvi va vh xong dua ve anh tif luu tai <task_id>_rvi_8days folder
        b8_arr = b8_arr.squeeze()  # (H, W)
        b4_arr = b4_arr.squeeze() 

        # calc NDVI and cloud Mask
        ndvi = self.calc_NDVI(b4_arr, b8_arr)
        ndvi_masked = self.cloud_mask(ndvi, cls_arr)
        

        # saving image
        image_name = "ndvi_test.tif" # sua lai sau 
        save_dir = os.path.join(self.path_to_save_ndvi_image, image_name)
        os.makedirs(self.path_to_save_ndvi_image, exist_ok=True)    
    
        metadata.update({
            "count": ndvi_masked.shape[0],
            "dtype": ndvi_masked.dtype
        })
      
        with rasterio.open(save_dir, "w", **metadata) as dst:
            dst.write(ndvi_masked)

        logging.info(f"saved rvi to {save_dir}")

     
    
    def processing_all_image(self):

        #get all prefix name of file name tif image 
        prefix_name = self.get_prefix_of_file(collection='sentinel2')

        for prefix in prefix_name: 
            path_b4 = os.path.join(self.path_to_sentinel1_folder, f"{prefix}_B04.tif")
            path_b8 = os.path.join(self.path_to_sentinel1_folder, f"{prefix}_B08.tif")
            path_cloudmask = os.path.join(self.path_to_sentinel1_folder, f"{prefix}_omnicloudmask.tif")

            b4_arr_npy, b4_profile = self.tif_to_numpy(path_b4)
            b8_arr_npy, b8_profile = self.tif_to_numpy(path_b8)
            cls_arr_npy, cls_profile = self.tif_to_numpy(path_cloudmask)
            
            self.processing_single_image(b4_arr_npy, b8_arr_npy, cls_arr_npy, b4_profile)