#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Nov 19 13:14:42 2025

This script reads opendrift simulation output data and plots their trajectories color coded with particle origin
Plots one figure per month

@author: nsteiger
"""

# In[1]

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import netCDF4 as nc
from datetime import datetime
import gc
from matplotlib.collections import LineCollection

from multiprocessing import Process


# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/webapp/figures/trajectories/'
sim_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/output/reduced/'


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

# --- function to read drift_Data ------
def read_driftdata(drift_file):

    with nc.Dataset(drift_file, mode='r') as ds:

        timestamp = ds.variables['time'][:]
        formatted_times = [datetime.fromtimestamp(ts) for ts in timestamp]

        return {
            'lon': ds.variables['lon'][:],
            'lat': ds.variables['lat'][:],
            'age_seconds': ds.variables['age_seconds'][:],
            'area': ds.variables['area'][:],
            'time': formatted_times
        }

# ----- plotting function THIS VERSION WITH SEGMENTS IS MUCH FASTER THAN MY ORIGINAL ONE -----
def plot_trajectory_origen_age(drift_data, bathy_data, area_colors, area_labels, bathy_levels, age, areas_to_plot):

    fig, ax = plt.subplots(figsize=(5, 8))

    age_days = drift_data['age_seconds'] / (24 * 3600)
    idx_age = np.abs(age_days + age).argmin(axis=1)   # same as idx_old = np.isclose(age_days, -age, atol=0.01).argmax(axis=1)

    segments_by_area = {a: [] for a in areas_to_plot}

    for k in range(drift_data['lon'].shape[0]):

        idx = idx_age[k]
        area = drift_data['area'][k, idx]

        if area not in segments_by_area or idx < 2:
            continue

        segments_by_area[area].append(np.column_stack((drift_data['lon'][k, :idx],drift_data['lat'][k, :idx])))

    for area, segments in segments_by_area.items():

        if not segments:
            continue

        ax.add_collection(LineCollection(segments,colors=area_colors[area-1],linewidths=0.1))

    ax.contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'],
               levels=bathy_levels, colors='black', linewidths=0.5)

    ax.autoscale()
    

    ax.set_title(f"Trajectories of particles seeded in {drift_data['time'][10].strftime('%m/%Y')}")

    ax.legend(handles=[Patch(color=area_colors[i-1], label=area_labels[i-1])
                       for i in areas_to_plot],
              loc='lower right')

    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    
    #print(len(plt.get_fignums()))
    
    print(sum(len(v) for v in segments_by_area.values()))

    return fig, ax



# def plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,areas_to_plot):
 
#     fig, ax = plt.subplots(figsize=(5, 8))
        
            
#     # select lon at lat of all trajectories of given age
#     # age_days = drift_data['age_seconds'] / (24 * 3600)
       
#     # Loop over each area and color code trajectories that end in this area with corresponding color
#     # THIS COULD MAYBE BE AVOIDED IF WE ALREADY MODIFY THE .NC FILE
#     for mask_i in areas_to_plot:
#         for k in range(0,drift_data['lon'].shape[0],1):   
#             idx = np.isclose( drift_data['age_seconds'][k, :], -age*(24 * 3600), atol=0.01).argmax()
#             if drift_data['area'][k,idx]==mask_i:
#                 ax.plot(drift_data['lon'][k,:idx],drift_data['lat'][k,:idx],linewidth = .1,color=area_colors[mask_i-1])
               
#     # Plot bathymetry contours
#     ax.contour(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'],levels=bathy_levels,colors='black',linewidths=0.5) 

#     # Add grid and title
#     # ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)
#     ax.set_title(f"Trajectories of particles seeded in {drift_data['time'][0].strftime('%m/%Y')}")
          
#     # Add legend with colors of each area
#     patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in areas_to_plot]
#     ax.legend(handles=patches, loc='lower right')
#     ax.set_xlabel('longitude')
#     ax.set_ylabel('latitude')
    
#     # plt.rcParams.update({
#     #     "font.size": 9,
#     #     "axes.labelsize": 9,
#     #     "xtick.labelsize": 8,
#     #     "ytick.labelsize": 8
#     # })

#     return fig, ax


# In[2]
# ==========================================
# ---- Do the plotting here -------
# ===========================================

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)
masks_to_plot = [8,2,3,4,5,6,7,1]

# input to be changed by user
age = 90
yrs = np.arange(1999,2000)
mos= np.arange(1,13)


# put reading of data and plotting into one function
def process_month(yr,mo):
        sim_file = f'{sim_folder}Connectivity_backward_{yr}_{mo:02d}.nc'
        print(sim_file)
        drift_data = read_driftdata(sim_file)
        
        
        # plot each area separately
        try:
            for i_mask in masks_to_plot:
                fig, ax = plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,[i_mask])
                fig.tight_layout()
                fig.savefig(f'{plot_folder}/Trajectories_{yr}_{mo:02d}_{area_labels[i_mask-1]}.png',dpi=300,bbox_inches='tight')
                plt.close(fig)
                fig.clear()

                del ax
                del fig
                    
            # plot all trajectories together       
            fig, ax = plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,masks_to_plot)
            fig.tight_layout()
            fig.savefig(f'{plot_folder}/Trajectories_{yr}_{mo:02d}_all.png',dpi=300,bbox_inches='tight')
            plt.close(fig)
            fig.clear()

            del ax
            del fig
                    
  
        finally:
            del drift_data
            gc.collect()
            


# Loop over each year and each month using subprocess to avoid memory growth
for yr in yrs:
    for mo in mos:
        p = Process(
            target=process_month,
            args=(yr, mo)
        )
        p.start()
        p.join()    # operating system destroys the entire process and reclaims all memory




            




