import os
import ujson as json
import numpy as np
from scipy.signal import savgol_coeffs
from scipy.ndimage import convolve1d
import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import MinMaxScaler


class MyTrainSet(Dataset):
    def __init__(self, prepath):
        super(MyTrainSet, self).__init__()
        self.prepath = prepath
        self.content = open(self.prepath).readlines()

    def __len__(self):
        return len(self.content)

    def __getitem__(self, idx):
        # print(idx)
        rec = json.loads(self.content[idx])

        rec['is_train'] = 1
        return rec

class MyTestSet(Dataset):
    def __init__(self, prepath):
        super(MyTestSet, self).__init__()
        self.prepath = prepath
        self.content = open(self.prepath).readlines()

    def __len__(self):
        return len(self.content)

    def __getitem__(self, idx):
        rec = json.loads(self.content[idx])

        rec['is_train'] = 0
        return rec


def collate_fn(recs):
    forward = list(map(lambda x: x['forward'], recs))
    backward = list(map(lambda x: x['backward'], recs))
    # normalize SAR data
    scaler = MinMaxScaler(feature_range=(-1, 1))

    def to_tensor_dict(recs):

        # extract SAR temporal change trend
        coeffs_long_trend = savgol_coeffs(19, 2)
        values0 = np.array(list(map(lambda r: list(map(lambda x: x['values'], r)), recs)))
        sar1 = values0[:, :, 0]
        sar2 = values0[:, :, 1]
        bsize = values0.shape[0]
        for k in range(bsize):
            onesar1 = sar1[k:k+1, :].T
            onesar2 = sar2[k:k+1, :].T
            onesar1 = scaler.fit_transform(onesar1)
            onesar2 = scaler.fit_transform(onesar2)
            onesar1 = onesar1[:, 0]
            onesar2 = onesar2[:, 0]
            onesar10 = convolve1d(onesar1, coeffs_long_trend, mode="wrap")
            onesar20 = convolve1d(onesar2, coeffs_long_trend, mode="wrap")
            values0[k, :, 0] = onesar10
            values0[k, :, 1] = onesar20
        values = torch.FloatTensor(values0)

        # values = torch.FloatTensor(
        #     list(map(lambda r: list(map(lambda x: x['values'], r)), recs)))

        masks = torch.FloatTensor(
            list(map(lambda r: list(map(lambda x: x['masks'], r)), recs)))
        deltas = torch.FloatTensor(
            list(map(lambda r: list(map(lambda x: x['deltas'], r)), recs)))
        eval_masks = torch.FloatTensor(
            list(map(lambda r: list(map(lambda x: x['eval_masks'], r)), recs)))

        return {'values': values, 'masks': masks, 'deltas': deltas,'eval_masks': eval_masks}

    ret_dict = {
        'forward': to_tensor_dict(forward),
        'backward': to_tensor_dict(backward)
    }

    ret_dict['is_train'] = torch.FloatTensor(
        list(map(lambda x: x['is_train'], recs)))

    del forward, backward
    return ret_dict

def scale_feature(feature_data, missing_marker=None):
    """
    Scales a feature (batch_size, T) to [0, 1] using its own min/max,
    handling a potential missing_marker.
    """
    if missing_marker is not None:
        valid_mask = (feature_data != missing_marker) & (~np.isnan(feature_data))
    else:
        valid_mask = ~np.isnan(feature_data)

    if not np.any(valid_mask): # Handle case where all data is missing/NaN
        min_val = 0
        max_val = 1
        range_val = 1
    else:
        min_val = np.min(feature_data[valid_mask])
        max_val = np.max(feature_data[valid_mask])
        range_val = max_val - min_val if max_val != min_val else 1.0

    scaled_data = feature_data.copy()
    # Apply scaling only to valid data points
    scaled_data[valid_mask] = (feature_data[valid_mask] - min_val) / range_val
    # Clip just in case of floating point issues, ensure stays in [0, 1]
    # scaled_data[valid_mask] = np.clip(scaled_data[valid_mask], 0.0, 1.0) # Clip if needed

    # Preserve missing markers if they existed
    if missing_marker is not None:
       scaled_data[~valid_mask] = missing_marker

    # Note: The original code preserved -100 for LST. We replicate this.
    # If a different fill value is desired for scaled missing data, modify here.

    return scaled_data, min_val, max_val


def collate_fn_2(recs):
    forward = list(map(lambda x: x['forward'], recs))
    backward = list(map(lambda x: x['backward'], recs))

    def to_tensor_dict(recs_direction):
        # recs_direction is either 'forward' or 'backward' list

        # values0 shape: (batch_size, T, num_features=4)
        values0 = np.array(list(map(lambda r: list(map(lambda x: x['values'], r)), recs_direction)), dtype=np.float32)
        bsize = values0.shape[0]
        num_features = values0.shape[2] # Should be 4

        if num_features != 4:
            raise ValueError(f"Expected 4 features (NDVI, ERA5_T2M, ERA5_SKT, LST), but found {num_features}")

        # --- Feature Processing ---
        processed_values = np.zeros_like(values0)
        min_max_scaling_info = {} # Store min/max for potential unscaling later

        # 1. NDVI (Index 0) - Savitzky-Golay Filter
        coeffs_long_trend = savgol_coeffs(19, 2) # Example coefficients
        ndvi_original = values0[:, :, 0]
        ndvi_processed = np.zeros_like(ndvi_original)
        for k in range(bsize):
            ndvi_single_series = ndvi_original[k, :]
            # Apply Sav-Gol filter (handle potential NaNs if fillNA wasn't perfect)
            # Sav-Gol doesn't handle NaNs well by default. Ensure filled before this.
            ndvi_processed[k, :] = convolve1d(ndvi_single_series, coeffs_long_trend, mode="wrap")
        processed_values[:, :, 0] = ndvi_processed

        # 2. ERA5_T2M (Index 1) - MinMax Scaling
        era5_t2m_scaled, min_t2m, max_t2m = scale_feature(values0[:, :, 1], missing_marker=None) # Assume no marker after fillNA
        processed_values[:, :, 1] = era5_t2m_scaled
        min_max_scaling_info['era5_t2m'] = (min_t2m, max_t2m)

        # 3. ERA5_SKT (Index 2) - MinMax Scaling
        era5_skt_scaled, min_skt, max_skt = scale_feature(values0[:, :, 2], missing_marker=None) # Assume no marker after fillNA
        processed_values[:, :, 2] = era5_skt_scaled
        min_max_scaling_info['era5_skt'] = (min_skt, max_skt)

        # 4. LST (Index 3 - Target) - MinMax Scaling (handling -100 marker)
        # LST is both an input feature (potentially) and the target. Scale it for input.
        lst_scaled, min_lst, max_lst = scale_feature(values0[:, :, 3], missing_marker=-100.0)
        processed_values[:, :, 3] = lst_scaled
        min_max_scaling_info['lst'] = (min_lst, max_lst) # Store LST min/max separately

        # --- Convert to Tensors ---
        values = torch.FloatTensor(processed_values)

        # Masks and Deltas (Load directly, shapes should match preprocessed data)
        # masks shape: (batch_size, T) - Indicates LST observation validity
        masks = torch.FloatTensor(
            list(map(lambda r: list(map(lambda x: x['masks'], r)), recs_direction)))

        # deltas shape: (batch_size, T, num_features=4)
        deltas = torch.FloatTensor(
            list(map(lambda r: list(map(lambda x: x['deltas'], r)), recs_direction)))

        # eval_masks shape: (batch_size, T) - Indicates LST held-out points
        eval_masks = torch.FloatTensor(
            list(map(lambda r: list(map(lambda x: x['eval_masks'], r)), recs_direction)))

        # Original LST values might be needed if target is unscaled LST
        original_lst = torch.FloatTensor(values0[:, :, 3])

        return {'values': values,         # Processed features (scaled/filtered)
                'masks': masks,           # LST Observation mask
                'deltas': deltas,         # Deltas for each feature
                'eval_masks': eval_masks, # LST Evaluation mask
                "min_max": min_max_scaling_info, # Min/Max values used for scaling
                "original_lst": original_lst # Include original LST if needed for loss calculation
                }

    ret_dict = {
        'forward': to_tensor_dict(forward),
        'backward': to_tensor_dict(backward)
    }

    # Keep track of original LST min/max for unscaling if needed (use forward's)
    # Note: Forward and Backward should ideally have the same min/max if calculated over the whole batch
    ret_dict['lst_min_max'] = ret_dict['forward']['min_max']['lst']

    # Add is_train flag if present in records (optional)
    if 'is_train' in recs[0]:
         ret_dict['is_train'] = torch.FloatTensor(list(map(lambda x: x['is_train'], recs)))

    del forward, backward # Clean up intermediate lists
    return ret_dict

def get_train_loader(batch_size, prepath, shuffle=True):
    data_set = MyTrainSet(prepath)
    data_iter = DataLoader(dataset=data_set, \
                           batch_size=batch_size, \
                           num_workers=20, \
                           shuffle=shuffle, \
                           pin_memory=True, \
                           collate_fn=collate_fn
                           )
    return data_iter


def get_train_loader_LST(batch_size, prepath, shuffle=True):
    data_set = MyTrainSet(prepath)
    data_iter = DataLoader(dataset=data_set, \
                           batch_size=batch_size, \
                           num_workers=20, \
                           shuffle=shuffle, \
                           pin_memory=True, \
                           collate_fn=collate_fn_2
                           )
    return data_iter


def get_test_loader(batch_size, prepath, shuffle=False):
    data_set = MyTestSet(prepath)
    data_iter = DataLoader(dataset=data_set, \
                           batch_size=batch_size, \
                           num_workers=20, \
                           shuffle=shuffle, \
                           pin_memory=True, \
                           collate_fn=collate_fn
                           )

    return data_iter

def get_test_loader_LST(batch_size, prepath, shuffle=False):
    data_set = MyTestSet(prepath)
    data_iter = DataLoader(dataset=data_set, \
                           batch_size=batch_size, \
                           num_workers=20, \
                           shuffle=shuffle, \
                           pin_memory=True, \
                           collate_fn=collate_fn_2
                           )

    return data_iter

