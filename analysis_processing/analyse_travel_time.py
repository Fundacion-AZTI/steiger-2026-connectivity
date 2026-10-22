#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  2 14:22:40 2025

@author: nsteiger
"""


# In[1]
# This section is needed for all sections below - run it first
# following sections can be executed independently


# load necessary functions
import pandas as pd
import numpy as np
import netCDF4 as nc
from datetime import datetime



# --- paths ---- CHANGE THESE
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
out_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/travel_time/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/reduced/'


# -- general settings-----
legend_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
legend_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]


sim_name = 'coast_previous_seeding5days' 



# Choose which simulation to run
simulation_folder = '2026_01_08_seeding5days_1993-2024'  # Change this to the correct folder





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


def calc_time_since_left_each_area(drift_data,area_number=None):
    """
    For each area A, return (lon_seed, lat_seed, time_since_left_A) for every trajectory.
    'time_since_left_A' is measured at seeding time t0 (age_seconds ~ 0) for backward runs:
      time_since_left_A = t0 - t_exit, where t_exit is the time when area transitions A -> not A
      (taking the last such exit after the seeding index).
    If a trajectory never visited A -> NaN.
    If visited but did not leave within the window -> 'zero'.

    Parameters
    ----------
    drift_data : dict
        Expected keys:
          'area' : (ntraj, nt) numeric area ids, NaN allowed
          'age_seconds' : (ntraj, nt) float, ~0 at seeding time
          'time' : (nt,) datetime-like (Python datetime, pandas Timestamp, or numpy datetime64)
        Optional keys for seeding positions:
          'lon_seed', 'lat_seed' : (ntraj,) arrays of seeding lon/lat
          OR provide 'lon', 'lat' as (ntraj, nt) and we'll take lon[:, idx0], lat[:, idx0].
    area_number : list/array-like, optional
        The ordered list of areas (1 to 8) to report. If None, will derive from data (unique non-NaN).


    Returns
    -------
    per_area : dict[area] -> pandas.DataFrame
        Each DataFrame has columns ['lon', 'lat', 'time'] with one row per trajectory.
        'time' is in days (float) if return_days=True; otherwise a timedelta-like.
    """
    lon_all = np.asarray(drift_data['lon'])
    lat_all = np.asarray(drift_data['lat'])
    areas_mat = np.asarray(drift_data['area'])
    age = np.asarray(drift_data['age_seconds'])
    time = np.asarray(drift_data['time'])
    ntraj, nt = areas_mat.shape

    # Initialize seeding positions lon_seed and lat_seed
    lon_seed = np.full(ntraj, np.nan, dtype=float)
    lat_seed = np.full(ntraj, np.nan, dtype=float)
    area_seed = np.full(ntraj, np.nan, dtype=float)

    # Areas to report
    # Determine the set/order of areas
    if area_number is None:
        # Unique areas from data, excluding NaNs
        areas = np.unique(areas_mat[~np.isnan(areas_mat)])
        areas = areas.tolist()
    else:
        areas = list(area_number)

    nb_areas = len(areas)

    # Prepare output: for each area, we will fill (lon, lat, time) per traj
    # We'll compute times as float days if return_days; else store timedeltas in object dtype.
    times_matrix = np.full((ntraj, nb_areas), np.nan, dtype=float)

    for k in range(ntraj):
        age_row = age[k]
        idx_candidates = np.where(np.isclose(age_row, 0.0, atol=0.01))[0]
        idx0 = idx_candidates[0]
        t0 = time[idx0]

        # Fill seeding lon/lat if we derive them from lon/lat arrays
        lon_seed[k] = lon_all[k, idx0]
        lat_seed[k] = lat_all[k, idx0]

        arow = areas_mat[k]
        area_seed = arow[idx0]
        seen = {area_seed}

        # Record the index per area when parcel exited last area
        last_exit_idx = {}  # area -> i_exit (index of the first non-A after an A block)
        if idx0 < nt - 1:
            # changes where arow[i] != arow[i+1] starting from seeding index
            changes = np.flatnonzero(arow[idx0:nt - 1] != arow[idx0 + 1:nt]) + idx0
            # For each change i, if leaving A (arow[i] == A, arow[i+1] != A), store i+1
            for i in changes:
                a_curr = arow[i]
                a_next = arow[i + 1]
                # Skip NaNs for a_curr (can't leave 'NaN' area)
                if np.isnan(a_curr):
                    continue
            
                # If the area changed, we have exited a_curr and entered a_next
                # We don't care whether a_next is already seen for exit tracking of a_curr
                if a_next != a_curr:
                    # Track visited areas to gate future "first-entry" logic if you also need it:
                    if not np.isnan(a_next) and (a_next not in seen):
                        seen.add(a_next)
                        last_exit_idx[a_next] = i + 1  # overwrite to keep the *last* exit

 

        # Fill times for requested areas
        for m, A in enumerate(areas):
            if (A in last_exit_idx) and (A != area_seed):
                i_exit = last_exit_idx[A]
                t_exit = time[i_exit]
                # Compute t0 - t_exit (time since leaving A)
                td = t0 - t_exit
                times_matrix[k, m] = td.days 

            else:
                # Never visited A OR visited but no exit in window.
                # Distinguish by checking if it was ever in A after seeding.
                was_in_A = False
                if idx0 < nt:
                    # Any occurrence of A?
                    row_segment = arow[idx0:]
                    # Use equality even if floats; here A values typically are discrete labels
                    was_in_A = np.any(row_segment == A)

                if was_in_A:
                    times_matrix[k, m] = 0.0  
                else:
                    # Never passed A -> NaN as requested
                    times_matrix[k, m] = np.nan 

    # Build per-area outputs as DataFrames
    
    
    per_area = pd.DataFrame({
            'lon': np.repeat(lon_seed, nb_areas),
            'lat': np.repeat(lat_seed, nb_areas),
            'area': np.tile(areas, ntraj),
            'time': times_matrix.reshape(-1)  # flatten (ntraj*nb_areas,)
        })


    # per_area = {}
    # for m, A in enumerate(areas):
    #     df = pd.DataFrame({
    #         "lon": lon_seed,
    #         "lat": lat_seed,
    #         "time": times_matrix[:, m]
    #     })
    #     per_area[A] = df

    return per_area

# In[3]
# SCRIPT THAT ALLOWS LONG TABLES
# Calculate the time it has taken one particle to move from one area to its seeding position


mos = np.arange(1, 13)
yrs = np.arange(1994, 2025)
area_numbers = [1,2,3,4,5,6,7,8]


# load bathymetry files
bathy_data = read_bathymetry(bathy_file)



for yr in yrs:
    for mo in mos:
        
        sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
        drift_data = read_driftdata(sim_file)


        time_per_area = calc_time_since_left_each_area(drift_data, area_number=area_numbers)
        time_per_area["year"] = yr
        time_per_area["month"] = mo

        # Write one compact file per monthly output
        time_per_area.to_parquet(f"{out_folder}/Travel_time_from_area_to_seeding_{yr}_{mo:02d}.parquet",index=False)

        print(f"Saved {yr}-{mo:02d}")


# In[4]
# CALCULATE statistics of travel time
# duckdb is efficient way to calculate the statistics without loading variables in data space
import duckdb

con = duckdb.connect()

path = f"{out_folder}/Travel_time_from_area_to_seeding_*.parquet"

df_stats = con.execute("""
    SELECT
        area,
        lon,
        lat,
        AVG(time) AS time_mean,
        STDDEV_SAMP(time) AS time_std,
        COUNT(time) AS count
    FROM read_parquet(?)
    GROUP BY area, lon, lat
    ORDER BY area, lon, lat
""", [path]).df()

# save statistics
df_stats.to_csv(f'{out_folder}/time_area_lonlat_stats.csv', index=False)




