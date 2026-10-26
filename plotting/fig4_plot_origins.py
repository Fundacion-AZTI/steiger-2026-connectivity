#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jun 30 12:41:58 2026

@author: nsteiger
"""

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import netCDF4 as nc
from datetime import datetime


# # input to be changed by user
# yr = [2016,2021,2015]
# mo = [2]
# age = 90
# masks_to_plot = [8,2,3,4,5,6,7,1]


# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/origin/'


# -- general settings-----
area_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]

# ---- function to read bathymetry data ------
def read_bathymetry(bathy_file):
    bathy_data = nc.Dataset(bathy_file, model='r')
    return {
        'lon': bathy_data.variables['lon'][:],
        'lat': bathy_data.variables['lat'][:],
        'depth': bathy_data.variables['elevation'][:]
    }


def three_modes(col):
    vals, counts = np.unique(col, return_counts=True)
    order = np.argsort(-counts)  # sort by descending count
    
    first = vals[order[0]] if len(order) > 0 else np.nan
    second = vals[order[1]] if len(order) > 1 else np.nan
    third = vals[order[2]] if len(order) > 2 else np.nan
    
    return first, second, third


def plot_origin_particles(lon,lat,origin,bathy_data,area_colors,area_labels,bathy_levels,ax):

    # Plot particles color-coded by region
    for region_id in range(1,len(area_labels)+1):
        mask = origin == region_id
        ax.scatter(lon[mask], lat[mask], s=7, c=area_colors[region_id-1], label=area_labels[region_id-1])
    
    
    # Plot bathymetry contours
    ax.contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)

    # Add grid and title
    # ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)
    ax.set_xlim(lon.min(), lon.max())
    ax.set_ylim(lat.min(), lat.max())
    
    ax.set_xticks([-10,-8,-6,-4,-2])
    ax.set_yticks([42,44,46,48])
    
    plt.rcParams.update({
        "font.size": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8
    })


    return ax


# In[2] Plot origin maps

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

age = 7

mos = [2,5,8,11]
yrs = np.arange(1994, 2023)
seedings = np.arange(0,7)  # 7 seeds 0,1,2,3,4,5,6 exist -> 55706 / 7 = 7958 particles/ seed
create_figure = False

most_frequent_origin = {}

lbl = ['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)','(i)','(j)','(k)','(l)']
cnt=0;

fig, axs = plt.subplots(3, 4, figsize=(6.8,6.8), sharex=True, sharey=True) # subplots in a row
    
for i, mo in enumerate(mos):  # loop over seasons to get climatology
    origin_age_month = []
    longitude = []
    latitude = []
    for j, yr in enumerate(yrs):
        origin_file = f'{sim_folder}/Lon_Lat_Origin_{yr}_year.nc'
        origin_data = nc.Dataset(origin_file, model='r')
        month = origin_data['month'][:]
        mask_mo = month==mo
        lon_ini =  origin_data.variables['lon_00'][mask_mo,:]
        lat_ini =  origin_data.variables['lat_00'][mask_mo,:]
        origin_age =  origin_data.variables[f'origin_{age:02d}'][mask_mo,:]
        seed_age =  origin_data.variables[f'seed_{age:02d}'][mask_mo,:]
        
        for k, seed in enumerate(seedings):  #split up trajectories to only count the ones from same seeding and append them. should be 7958 particles per seeding
            mask = seed_age==seed
            longitude = lon_ini[mask]
            latitude = lat_ini[mask]
            origin_age_month.append(origin_age[mask])

    # Convert to 2D array
    all_origin_ages = np.array(origin_age_month)

    origin_first_mode, origin_second_mode, origin_third_mode = np.apply_along_axis(three_modes, axis=0, arr = all_origin_ages)
    
    # plot 1st mode
    ax=axs[0,i]
    ax = plot_origin_particles(longitude, latitude, origin_first_mode,bathy_data,area_colors,area_labels,bathy_levels,ax)
    #ax.set_xlabel('longitude')
    ax.text(-2.8,47.8,lbl[cnt])
    if i==0:
        ax.set_ylabel('latitude')
    
    # plot 2nd mode
    ax=axs[1,i]
    ax = plot_origin_particles(longitude, latitude, origin_second_mode,bathy_data,area_colors,area_labels,bathy_levels,ax)
    #ax.set_xlabel('longitude')
    ax.text(-2.8,47.8,lbl[cnt+4])
    if i==0:
        ax.set_ylabel('latitude')  

    # plot 2nd mode
    ax=axs[2,i]
    ax = plot_origin_particles(longitude, latitude, origin_third_mode,bathy_data,area_colors,area_labels,bathy_levels,ax)
    ax.set_xlabel('longitude')
    ax.text(-2.8,47.8,lbl[cnt+8])
    if i==0:
        ax.set_ylabel('latitude') 
        
    cnt=cnt+1;
    
    
#patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in masks_to_plot]
#ax.legend(handles=patches, loc='lower right',fontsize=8)     


# save figure
fig.tight_layout()
fig.savefig(f'{plot_folder}/Figure_4_Particle_origin_{age}days.png')        
 


