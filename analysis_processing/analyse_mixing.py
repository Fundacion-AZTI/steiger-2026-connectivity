#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Mar 18 07:30:07 2026

@author: nsteiger
"""

# In[1]
# This section is needed for all sections below - run it first
# following sections can be executed independently

# load necessary functions
import numpy as np
import xarray as xr
import netCDF4 as nc
from datetime import datetime
from scipy import sparse



# --- paths ----  CHANGE THIS TO CORRESPONDING FILE AND FOLDER
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
out_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/mixing/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/reduced/'


# -- general settings-----
area_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]



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

# Call here function to calculate mixing index
def compute_mixing(drift_data, age):
    lat_bins, lon_bins, mixing_index = calculate_mixing_index_fast(drift_data, age)
    mixing_index = mixing_index.astype(float)
    mixing_index[mixing_index > 10] = np.nan
    
    lat_centers = 0.5 * (lat_bins[:-1] + lat_bins[1:])
    lon_centers = 0.5 * (lon_bins[:-1] + lon_bins[1:])

    return lat_centers, lon_centers, mixing_index


# --- function to calculate mixing index -----------------------
def calculate_mixing_index_fast(drift_data,age):
# mixing index is calculated by checking for a regular lon/lat grid within the simulation area, 
# how many different origins the particles have that pass through this grid

    age_days = drift_data['age_seconds'] / (24 * 3600)

    lon_min, lon_max = -13, -1
    lat_min, lat_max = 38.9, 50.6

    # Find indices corresponding to age 0 and -age once for all particles
    idx0 = np.argmax(np.isclose(age_days, 0, atol=0.01), axis=1)
    idxA = np.argmax(np.isclose(age_days, -age, atol=0.01), axis=1)

    # Build a mask selecting the segment for each particle
    # mask[k, i] = True if idx0[k] <= i < idxA[k]
    time_steps = age_days.shape[1]
    step_idx = np.arange(time_steps)
    mask = (step_idx >= idx0[:, None]) & (step_idx < idxA[:, None])

    # Extract segments using mask
    lon_flat = drift_data['lon'][mask]
    lat_flat = drift_data['lat'][mask]
    
    
    # origin at idxA for each particle (shape: N,)
    origin_per_particle = drift_data['area'][np.arange(mask.shape[0]), idxA]
    # how many time steps each particle contributes
    counts = mask.sum(axis=1)
    # repeat origins according to mask row counts
    origin_flat = np.repeat(origin_per_particle, counts)

    
    # Create regular grid
    lat_bins = np.linspace(lat_min, lat_max, 100)
    lon_bins = np.linspace(lon_min, lon_max, 100)

    # Compute bin indices for all points (vectorized)
    i = np.searchsorted(lat_bins, lat_flat) - 1
    j = np.searchsorted(lon_bins, lon_flat) - 1

    n_lat = len(lat_bins) - 1
    n_lon = len(lon_bins) - 1
    valid = (i >= 0) & (j >= 0) & (i < n_lat) & (j < n_lon)

    i = i[valid]
    j = j[valid]
    origins = origin_flat[valid]

    # Use sparse matrix to aggregate unique origins per cell
    # rows encode (i, j) combined into one index
    row_index = i * n_lon + j

    M = sparse.coo_matrix(
        (origins, (row_index, np.zeros_like(row_index))),
        shape=(n_lat*n_lon, 1)
    )

    # Now group by grid cell: count unique origins per cell
    # Convert COO rows into bins
    mixing_index = np.zeros(n_lat*n_lon, dtype=int)

    for cell in range(n_lat*n_lon):
        vals = M.data[M.row == cell]
        mixing_index[cell] = len(np.unique(vals))

    mixing_index = mixing_index.reshape((n_lat, n_lon))

    return lat_bins, lon_bins, mixing_index



# In[3] -- start calculation ----- 

# ---- loop over all years and months ------
mos = np.arange(1, 13)
yrs = np.arange(1994, 2025)

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)


for yr in yrs:
    
    # temporary containers for each age class
    mixing_results = {
        7: [],
        30: [],
        90: []
    }

    lat_bins_ref = None
    lon_bins_ref = None

    for mo in mos:

        sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
        drift_data = read_driftdata(sim_file)

        for age in (7, 30, 90):
            lat_bins, lon_bins, mix = compute_mixing(drift_data, age)

            # store the bins once (they shouldn't change)
            if lat_bins_ref is None:
                lat_bins_ref = lat_bins
                lon_bins_ref = lon_bins

            mixing_results[age].append(mix)

    # Save to NetCDF for each age class
    for age in (7, 30, 90):

        # Convert to DataArray
        mixing_array = xr.DataArray(
            np.stack(mixing_results[age], axis=0),  # shape = (month, lat, lon)
            dims=("month", "lat", "lon"),
            coords={
                "month": mos,
                "lat_bins": ("lat", lat_bins_ref),
                "lon_bins": ("lon", lon_bins_ref)
            },
            name="mixing"
        )

        ds = xr.Dataset({"mixing": mixing_array})

        # # Save file
        out_file = f"{out_folder}/mixing_{age}_{yr}.nc"
        # ds.to_netcdf(out_file)

        print(f"Saved: {out_file}")



        
