#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 24 12:18:10 2026

@author: nsteiger
"""



# load necessary functions

import numpy as np
import xarray as xr
import matplotlib.path as mpath
from scipy.interpolate import RegularGridInterpolator   
import pandas as pd
import netCDF4 as nc


import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# load necessary functions
from modules.load_config import load_config


# --- paths ---- CHANGE THIS TO CORRESPONDING DATA AND FOLDERS
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
out_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/reduced/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/'


# -- general settings-----
legend_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
legend_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]

sim_name= 'coast_previous_seeding5days'




# In[2]

def read_bathymetry(bathy_file):
    bathy_data = nc.Dataset(bathy_file, model='r')
    return {
        'lon': bathy_data.variables['lon'][:],
        'lat': bathy_data.variables['lat'][:],
        'depth': bathy_data.variables['elevation'][:]
    }

from datetime import datetime
def read_driftdata(drift_file):
    drift_data = nc.Dataset(drift_file, model='r')
    timestamp = drift_data.variables['time'][:]
    formatted_times = [datetime.fromtimestamp(ts) for ts in timestamp]
    if 'status' in drift_data.variables:
        return {
            'lon': drift_data.variables['lon'][:],
            'lat': drift_data.variables['lat'][:],
            'age_seconds': drift_data.variables['age_seconds'][:],
            'origin_marker': drift_data.variables['origin_marker'][:],
            'status': drift_data.variables['status'][:],
            'time': formatted_times
        }
    else:
        return {
            'lon': drift_data.variables['lon'][:],
            'lat': drift_data.variables['lat'][:],
            'age_seconds': drift_data.variables['age_seconds'][:],
            'origin_marker': drift_data.variables['origin_marker'][:],
            'time': formatted_times
        }     

# ------------------------------------------------------------------------
# ---------------------------------------------------------------
# function to define the areas within the BoB for connectivity
def mask_regions_BoB(lon_min,lon_max,lat_min,lat_max,bathy_data,res,d_shelf=-200,d_deep=-1000):
    
    
    #create mashgrid of bathymetry lon/lat
    lat_grid, lon_grid = np.meshgrid(bathy_data['lat'], bathy_data['lon'], indexing='ij')
    
    # Define polygon points for Spanish region (simplified)
    spanish_polygon = mpath.Path([
        (-10.0, 45.0),  # Western Spanish coast
        (-4.0, 45.0),
        (-3.0, 43.7),
        (-1.8, 43.6),
        (-1.2, 43.65),
        (lon_max+res, 43.65),
        (lon_max+res, lat_min-res),
        (lon_min-res, lat_min-res),
        (-10.0, 45.0)   # Close polygon
    ])
    
    # Create mask for Spanish region
    points = np.vstack((lon_grid.ravel(), lat_grid.ravel())).T
    in_spanish = spanish_polygon.contains_points(points).reshape(lat_grid.shape)
    



    # create all masks
    mask = np.full(bathy_data['depth'].shape, np.nan)
    # southern boundary
    mask_A1 = mask.copy()
    mask_A1[(lat_grid<lat_min) & (lon_grid>=lon_min)] =1
    # western boundary (open ocean)
    mask_A2 = mask.copy()
    mask_A2[lon_grid<lon_min]=1
    # northern boundary
    mask_A3 = mask.copy()
    mask_A3[(lat_grid>lat_max)& (lon_grid>=lon_min)]=1
    
    # cont. shelf French coast
    mask_A4 = mask.copy()
    mask_A4[(bathy_data['depth']<0) & (bathy_data['depth']>d_shelf) & (~in_spanish) & (lat_grid<=lat_max) & (lat_grid>=lat_min)]=1
    # shelf break French coast
    mask_A6 = mask.copy()
    mask_A6[(bathy_data['depth']<=d_shelf) & (bathy_data['depth']>d_deep) & (~in_spanish) & (lat_grid<=lat_max) & (lat_grid>=lat_min)]=1     
    # cont. shelf Spanish coast
    mask_A5 = mask.copy()
    mask_A5[(bathy_data['depth']<0) & (bathy_data['depth']>d_shelf) & (in_spanish) & (lat_grid>=lat_min)]=1    
    # shelf break Spanish coast
    mask_A7 = mask.copy()
    mask_A7[(bathy_data['depth']<=d_shelf) & (bathy_data['depth']>d_deep) & (in_spanish) & (lat_grid>=lat_min)]=1
        
    # deep ocean within BoB
    mask_A8 = mask.copy()
    mask_A8[(bathy_data['depth']<=d_deep) & (lon_grid>=lon_min)  & (lat_grid<=lat_max) & (lat_grid>=lat_min)]=1
    
    #save masks as list
    masks = []
    masks.append(mask_A1)
    masks.append(mask_A2)
    masks.append(mask_A3)
    masks.append(mask_A4)
    masks.append(mask_A5)
    masks.append(mask_A6)
    masks.append(mask_A7)
    masks.append(mask_A8)
    
    return masks




# ---------------------------------------------------------------
# appoint area of BoB to trajectory at each point in time
def assign_area_trajectories(bathy_data,drift_data,masks):
    mask_interpolators = [
        RegularGridInterpolator((bathy_data['lat'], bathy_data['lon']), mask_i, method='nearest', bounds_error=False, fill_value=np.nan)
        for mask_i in masks
    ]
           
    # Flatten trajectory coordinates
    coords = np.stack([drift_data['lat'].ravel(), drift_data['lon'].ravel()], axis=-1)  # shape: (N, 2), where N = num_trajectories × num_timesteps

    # Initialize flat area array
    flat_area = np.zeros(coords.shape[0], dtype=int)

    # Loop over masks 
    for k, mask_interp in enumerate(mask_interpolators):
        flat_values = mask_interp(coords)  # shape: (N,)
        matched = (flat_values > 0) & (flat_area == 0)  # only assign if not already matched
        flat_area[matched] = k + 1  # 1-indexed

    # Reshape back to original trajectory shape
    area = flat_area.reshape(drift_data['lat'].shape)  
    
    
    # the following is new to fill area0 values correctly
    #fill all 0 values for area with previous value (for stranded particles)     
    area_df = pd.DataFrame(area).replace(0, np.nan)

    # Forward fill along time (axis=1)
    area_filled = area_df.ffill(axis=1).values  
    # note that nans at the beginning will remain nan, which is good because this happens for particles that get seeded later and are masked

#    #Extend the area for all stranded particles to assume they stay in the area where they stranded
#    for k in range(drift_data['lon'].shape[0]):  # loop over all trajectories
#        if np.sum(area[k, :]==0)>0: # if trajectory has no area assigned at any point in time (area = 0)
#            indices = np.where(area[k,:]==0)[0]  #find indeces in k where area = 0
#            #if indices[0] > 0:
#            area[k,area[k,:]==0] = area[k,indices[0]-1] #replace all 0 with last non-zero value


#    # still a few trajectories remain that start with area 0 but move into an area > 0
#    indices = np.where(np.sum(area == 0, axis=1) > 0)[0]
#    for k in indices:
#        area[k,:] = area[k,:].max()
    
        
    
    # Convert area to a masked array using the same mask as lon
    area_masked = np.ma.masked_array(area_filled, mask=drift_data['lon'].mask)
    
        
    drift_data['area'] = area_masked
    print(drift_data)
    
    return drift_data




# In[3] loop over all simulations
mo = np.arange(1,13)
yr = np.arange(1994,2025)


# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

# Load the config for the selected simulation
config = load_config(sim_folder)
config.fname= 'coast_previous_seeding5days'
masks = mask_regions_BoB(config.lon_min,config.lon_max,config.lat_min,config.lat_max,bathy_data,config.res)

for i, yrs in enumerate(yr):
    for j, mos in enumerate(mo):
        out_file = f'{sim_folder}/Connectivity_ibi_backward_0.08deg_-900s_{yrs}_{mos:02d}_{sim_name}.nc'
        print(f"Processing: {out_file}")
        
        # calculate origin area for each trajectory
        drift_data = read_driftdata(out_file)
        drift_data = assign_area_trajectories(bathy_data,drift_data,masks)
        drift_data['area'] = np.asarray(drift_data['area'], dtype=np.int32)

        # load data with xarray
        ds = xr.open_dataset(out_file)
        ds = ds.drop_vars([
            'status',
            'moving',
            'origin_marker',
            'trajectory'
        ])
        
        # add variable area to not read it in every plotting function
        ds['area'] = xr.DataArray(
            drift_data['area'],
            dims=('trajectory','time'),
            attrs={
                'long_name': 'Origin area classification'
            }
        )
        
        
        # specify compression level
        encoding = {
            var: {
                'zlib': True,
                'complevel': 4,
                'shuffle': True
            }
            for var in ds.data_vars
        }

        # save monthly data
        ds.to_netcdf(
            f'{out_folder}/Connectivity_backward_{yrs}_{mos:02d}.nc',
            format='NETCDF4',
            encoding=encoding
        )





        
