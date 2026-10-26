#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 13:52:59 2026

Plot map of subareas and seeding locations

@author: nsteiger
"""

# In[1]

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import netCDF4 as nc
from datetime import datetime

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/reduced/'


# -- general settings-----
area_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]

lon_min = -11
lon_max = -1
lat_min = 41
lat_max = 48.5
res = 0.08


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

# plot areas of BoB together with locations of particles of certain age in black
def plot_masks_particles_age(bathy_data,masks,drift_data,bathy_levels,age,legend_colors,legend_labels,areas=[3,4,5,6,7,0,1,2]):

    lat_grid, lon_grid = np.meshgrid(bathy_data['lat'], bathy_data['lon'], indexing='ij')
    
    # select lon at lat of all trajectories of given age
    age_days = drift_data['age_seconds'] / (24 * 3600)
    mask = np.isclose(age_days, -age, atol=0.01)  # tolerance for floating-point
    lat_at_age = np.where(mask, drift_data['lat'], np.nan)
    lon_at_age = np.where(mask, drift_data['lon'], np.nan)
    
    for i in areas:
        plt.contourf(lon_grid, lat_grid, masks[i], levels=[0.5, 1.5], colors=legend_colors[i])
    plt.scatter(lon_at_age,lat_at_age,marker='.',color='black',s=0.3)
    plt.contour(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'],levels=bathy_levels,colors='black',linewidths=0.5)
    
    
    # Define two levels: sea (<=0) and land (>0) 
    levels = [-1e9, 0, 1e9] # anything below 0, and anything above 0 
    # Colors: ocean = transparent or blue, land = white 
    colors = ['none', 'white'] # or ['lightblue', 'white'] 
    plt.contourf(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'], levels=levels, colors=colors)
    plt.contour(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'],levels=[0],colors='black',linewidths=1)

    patches = [Patch(color=color, label=label) for color, label in zip(legend_colors, legend_labels)]
    plt.legend(handles=patches, loc='lower right',fontsize=7)
    
    plt.xlim(lon_grid.min(),lon_grid.max())
    plt.ylim(lat_grid.min(),lat_grid.max())
    
    plt.xlabel('longitude')
    plt.ylabel('latitude')
    
    plt.rcParams.update({
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7
    })

    return plt



# In[2]
# Plot map of BoB with colored areas and seeding locations

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

sim_file = f'{sim_folder}/Connectivity_backward_1994_02.nc'
drift_data = read_driftdata(sim_file)

# create masks for regions of BoB
from analysis.connectivity_functions import mask_regions_BoB
masks = mask_regions_BoB(lon_min,lon_max,lat_min,lat_max,bathy_data,res)


age = 0
plt.figure(figsize=(3.3,4.5))
plt = plot_masks_particles_age(bathy_data,masks,drift_data,bathy_levels,age,area_colors,area_labels,areas=[3,4,5,6,7,0,1,2])
plt.tight_layout()
plt.savefig(f'{plot_folder}/Figure1_Map_areas_seeding_at_t0.png',dpi=300,bbox_inches="tight")


# In[3]
# Count particles in each area

seedings = np.arange(0,7)  
yr = 1994
mo=1

origin_file = f'/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/origin/Lon_Lat_Origin_{yr}_year.nc'
origin_data = nc.Dataset(origin_file, model='r')
month = origin_data['month'][:]
mask_mo = month==mo
lon_ini =  origin_data.variables['lon_00'][mask_mo,:]
lat_ini =  origin_data.variables['lat_00'][mask_mo,:]
origin_age =  origin_data.variables['origin_00'][mask_mo,:]
seed_age =  origin_data.variables['seed_00'][mask_mo,:]

origin_per_seed = []
longitude_per_seed = []
latitude_per_seed = []

mask = seed_age==1
longitude_per_seed = lon_ini[mask]
latitude_per_seed = lat_ini[mask]
origin_per_seed = origin_age[mask]
    

for region_id,label in enumerate(area_labels):
    mask = origin_per_seed == region_id+1
    print(label)
    print(len(longitude_per_seed[mask]))
    
      
