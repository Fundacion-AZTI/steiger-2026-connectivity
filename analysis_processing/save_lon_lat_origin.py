#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jan 22 12:23:30 2026

@author: nsteiger
"""

# In[1]
# This section is needed for all sections below - run it first
# following sections can be executed independently
import numpy as np
import xarray as xr
import netCDF4 as nc
from datetime import datetime




# --- paths ---- CHANGE THIS TO CORREPSONDING FILE AND FOLDER
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
out_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/origin/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/reduced/'


# -- general settings-----
legend_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
legend_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]

sim_name= 'coast_previous_seeding5days'




# In[2] -----functions ------ 
# ---- function to read bathymetry data ------
def read_bathymetry(bathy_file):
    bathy_data = nc.Dataset(bathy_file, model='r')
    return {
        'lon': bathy_data.variables['lon'][:],
        'lat': bathy_data.variables['lat'][:],
        'depth': bathy_data.variables['elevation'][:]
    }

# --- function to read drift_Data ------
def read_driftdata(drift_file):
    drift_data = nc.Dataset(drift_file, model='r')
    timestamp = drift_data.variables['time'][:]
    formatted_times = [datetime.fromtimestamp(ts) for ts in timestamp]
    return {
        'lon': drift_data.variables['lon'][:],
        'lat': drift_data.variables['lat'][:],
        'age_seconds': drift_data.variables['age_seconds'][:],
        'area': drift_data.variables['area'][:],
        'time': formatted_times
    }

    
# --- function to extract origin .--------
def calculate_lon_lat_origin_new(drift_data,age):
    # here we don't calculate initial lon lat origin, but it has to be calculated with age = 0
    
    # select lon at lat of all trajectories of given age
    age_days = drift_data['age_seconds'] / (24 * 3600)
    time_rep = np.tile(drift_data['time'],(len(drift_data['lon']),1))


    mask = np.isclose(age_days, -age, atol=0.01)  # tolerance for floating-point
    lon_at_age = drift_data['lon'][mask]
    lat_at_age = drift_data['lat'][mask]
    area_at_age = drift_data['area'][mask]
    seed_at_age = drift_data['origin_marker'][mask]
    time_at_age = time_rep[mask]
    
    lon_age = lon_at_age.data
    lat_age = lat_at_age.data
    area_age = area_at_age.data
    seed_age = seed_at_age.data
    time_age = time_at_age
    
    #lon_age = lon_at_age[~np.isnan(lon_at_age)] # shape (trajectory,)
    #lat_age = lat_at_age[~np.isnan(lat_at_age)] # shape (trajectory,)
    #area_age = area_at_age[~np.isnan(area_at_age)] # shape (trajectory,)
    origin_age = area_age.astype(int) # shape (trajectory,)


    return lat_age, lon_age, origin_age, time_age, seed_age

# In[2]

mos = np.arange(1, 13)
yrs = np.arange(1994, 2025)
ages = [0, 7, 30, 90]

n_seeds = 6  # 6 seedings per month

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)



for yr in yrs:
    print(f"\n=== Processing YEAR {yr} ===")

    # Temporary storage as list of columns → final concat along time axis
    data_dict = {
        'lon_00': [], 'lat_00': [], 'seed_00':[], 'time_00': [], 'origin_00': [],
        'lon_07': [], 'lat_07': [], 'seed_07':[], 'time_07': [], 'origin_07': [],
        'lon_30': [], 'lat_30': [], 'seed_30':[], 'time_30': [], 'origin_30': [],
        'lon_90': [], 'lat_90': [], 'seed_90':[], 'time_90': [], 'origin_90': []
    }

    for mo in mos:
        sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
        drift_data = read_driftdata(sim_file)
        
        print(f"  -> {yr}-{mo:02d} : {sim_file}")


        # Age-dependent variables
        for age in ages:
            lat_age, lon_age, origin_age, time_age, seed_age = calculate_lon_lat_origin_new(drift_data,age)

            tag = f"{age:02d}"

            data_dict[f'lon_{tag}'].append(np.asarray(lon_age))
            data_dict[f'lat_{tag}'].append(np.asarray(lat_age))
            data_dict[f'seed_{tag}'].append(np.asarray(seed_age))
            data_dict[f'time_{tag}'].append(np.asarray(time_age))
            data_dict[f'origin_{tag}'].append(np.asarray(origin_age))

    
    # After the loop (for each tag you filled)
    for key in list(data_dict.keys()):
        arr = np.stack(data_dict[key], axis=0)  # (N, T)
        data_dict[key] = arr
        T, N = arr.shape
        print(f" -> Final shape for {yr}, {key}: time={T}, trajectory={N}")


    # Build dataset
    ds = xr.Dataset(
        {key: (['month', 'trajectory'], data_dict[key]) for key in data_dict},
        coords={
            'month': mos,
            'trajectory': np.arange(N)
        }
    )

    encoding = {var: {"zlib": True, "complevel": 4} for var in ds.data_vars}

    outname = f"Lon_Lat_Origin_{yr}_year.nc"
    ds.to_netcdf(f'{out_folder}/{outname}', encoding=encoding)

    print(f"✔ Saved yearly file: {outname}")

