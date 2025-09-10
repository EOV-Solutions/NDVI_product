import rasterio
from datetime import datetime
import os 
from processing_raw_image.processing_abstract import ProcessingImage
import numpy as np
from logger.Logger import app_logger as logging
""" 
    NOTE: Sentinel 1 file co 2 bands VV va VH: format ten nhu sau <MA TEN>_<StartDate>_<EndDate>_<>_<>_vh(vv).tif 
        Truy xuat: VH: <Maten>_*_vh.tif, VV: <Maten>_*_vv.tif
"""
class ProcessSentinel1(ProcessingImage):
    def __init__(self, path_to_folder, task_id):
        super().__init__(path_to_folder, task_id)
        self.path_to_sentinel1_folder = os.path.join(self.path_to_folder, "raw/sentinel1")
        self.path_to_save_rvi_image = os.path.join(self.path_to_folder, f"processed/{self.task_id}_rvi_8days")

    def calc_RVI(self, vh_arr, vv_arr):
        rvi_arr = (4 * vh_arr) / (vv_arr + vh_arr + 1e-5)
        return rvi_arr

    def processing_single_image(self, vh_arr, vv_arr, metadata):
        # stack rvi va vh xong dua ve anh tif luu tai <task_id>_rvi_8days folder
        vv_arr = vv_arr.squeeze()  # (H, W)
        vh_arr = vh_arr.squeeze() 
        rvi = self.calc_RVI(vh_arr, vv_arr)

        
        stacked_img = np.stack([rvi, vh_arr], axis=0)

        image_name = "rvi_test.tif" # sua lai sau 
        save_dir = os.path.join(self.path_to_save_rvi_image, image_name)
        os.makedirs(self.path_to_save_rvi_image, exist_ok=True)    
    
        metadata.update({
            "count": stacked_img.shape[0],
            "dtype": stacked_img.dtype
        })
      
        with rasterio.open(save_dir, "w", **metadata) as dst:
            dst.write(stacked_img)

        logging.info(f"saved rvi to {save_dir}")

     
    
    def processing_all_image(self):
        prefix_name = self.get_prefix_of_file(collection='sentinel1')
        for prefix in prefix_name: 
            path_vv = os.path.join(self.path_to_sentinel1_folder, f"{prefix}_vv.tif")
            path_vh = os.path.join(self.path_to_sentinel1_folder, f"{prefix}_vh.tif")

            vv_arr_npy, vv_profile = self.tif_to_numpy(path_vv)
            vh_arr_npy, vh_profile = self.tif_to_numpy(path_vh)

            self.processing_single_image(vh_arr_npy, vv_arr_npy, vh_profile)