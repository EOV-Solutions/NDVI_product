from __future__ import annotations
from abc import ABC, abstractmethod
import os 
import rasterio
import numpy as np

class ProcessingImage(ABC):


    def __init__(self, path_to_folder, task_id):
        self.path_to_folder = path_to_folder #(path to folder)
        self.folder_save = 'processed'
        self.path_to_folder_processed = os.path.join(self.path_to_folder, self.folder_save)
        self.task_id = task_id
   

   
    def tif_to_numpy(self, path_to_image):
        with rasterio.open(path_to_image) as src:
            image_array  = src.read()
            profile = src.profile 
        return image_array, profile    
    
  
    def get_prefix_of_file(self, collection):
        # get in folder raw 
        path_to_raw_image = os.path.join(self.path_to_folder, 'raw', collection)
        list_name_image = os.listdir(path_to_raw_image)
        
        list_prefix = []
        for name in list_name_image:
            list_prefix.append('_'.join(name.split('.')[0].split('_')[:-1]))

        unique_prefix_name = list(dict.fromkeys(list_prefix))

        return unique_prefix_name
    
