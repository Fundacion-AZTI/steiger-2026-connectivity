#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 12:54:39 2026

This script reads opendrift simulation output data and plots their trajectories for all years

@author: nsteiger
"""


# In[1]

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch
import netCDF4 as nc
from datetime import datetime


# input to be changed by user
age = 90
masks_to_plot = [8,2,3,4,5,6,7,1]


# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
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

# ----- plotting function -----
def plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,areas_to_plot=[2,8,1,3,4,5,6,7]):
 

    # select lon at lat of all trajectories of given age
    age_days = drift_data['age_seconds'] / (24 * 3600)
       
    # Loop over each area and color code trajectories that end in this area with corresponding color
    # THIS COULD MAYBE BE AVOIDED IF WE ALREADY MODIFY THE .NC FILE
    for mask_i in areas_to_plot:
        for k in range(0,drift_data['lon'].shape[0],6):   #only plot every 3rd trajectory for better visibility
            idx = np.isclose(age_days[k, :], -age, atol=0.01).argmax()
            if drift_data['area'][k,idx]==mask_i:
                ax.plot(drift_data['lon'][k,:idx],drift_data['lat'][k,:idx],linewidth = .1,color=area_colors[mask_i-1])
               
    # Plot bathymetry contours
    ax.contour(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'],levels=bathy_levels,colors='black',linewidths=0.5) 


    # Add legend with colors of each area
    #patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in areas_to_plot]
    #ax.legend(handles=patches, loc='lower right',fontsize=6)
    ax.set_xlabel('longitude')
    ax.set_ylabel('latitude')
    
    
    plt.rcParams.update({
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 7,
        "ytick.labelsize": 7
    })

        

    return ax


# In[2]
# ==========================================
# ---- Do the plotting here -------
# ===========================================


# load bathymetry files
bathy_data = read_bathymetry(bathy_file)


# First plot for 1994 - 2003
yrs = np.arange(1994,2004)
mos = [2,5,8,11]
fig, axs = plt.subplots(len(mos), len(yrs), figsize=(8,5), sharex=True, sharey=True)
for i, yr in enumerate(yrs):
    for j, mo in enumerate(mos):
        sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
        drift_data = read_driftdata(sim_file)
        ax=axs[j, i]
        plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,masks_to_plot)
        if i>0:
            ax.set_ylabel('')
        if j<3:
            ax.set_xlabel('')

#patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in masks_to_plot]
#ax.legend(handles=patches, loc='lower right',fontsize=6)     
fig.tight_layout()
fig.savefig(f'{plot_folder}/Figure_A1_Trajectory_particles_origin_1994-2003.png',dpi=300)

# In[3]
# -----------------------------------------------------
# Next plot for 2004 - 2013
yrs = np.arange(2004,2014)
mos = [2,5,8,11]
fig, axs = plt.subplots(len(mos), len(yrs), figsize=(8,5), sharex=True, sharey=True)
for i, yr in enumerate(yrs):
    for j, mo in enumerate(mos):
        sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
        drift_data = read_driftdata(sim_file)
        ax=axs[j, i]
        plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,masks_to_plot)
        if i>0:
            ax.set_ylabel('')
        if j<3:
            ax.set_xlabel('')

#patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in masks_to_plot]
#ax.legend(handles=patches, loc='lower right',fontsize=6)     
fig.tight_layout()
fig.savefig(f'{plot_folder}/Figure_A1_Trajectory_particles_origin_2004-2013.png',dpi=300)


# In[4]
# ---------------------------------------------------
# Next plot for 2014 - 2023
yrs = np.arange(2014,2024)
mos = [2,5,8,11]
fig, axs = plt.subplots(len(mos), len(yrs), figsize=(8,5), sharex=True, sharey=True)
for i, yr in enumerate(yrs):
    for j, mo in enumerate(mos):
        sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
        drift_data = read_driftdata(sim_file)
        ax=axs[j, i]
        plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,masks_to_plot)
        if i>0:
            ax.set_ylabel('')
        if j<3:
            ax.set_xlabel('')

#patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in masks_to_plot]
#ax.legend(handles=patches, loc='lower right',fontsize=6)     
fig.tight_layout()
fig.savefig(f'{plot_folder}/Figure_A1_Trajectory_particles_origin_2014-2023.png',dpi=300)





