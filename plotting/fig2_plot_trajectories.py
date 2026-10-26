#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun 29 11:14:42 2026

This script reads opendrift simulation output data and plots their trajectories 

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
yr = [2016,2021,2015]
mo = [2]
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
        for k in range(0,drift_data['lon'].shape[0],3):   #only plot every 3rd trajectory for better visibility
            idx = np.isclose(age_days[k, :], -age, atol=0.01).argmax()
            if drift_data['area'][k,idx]==mask_i:
                ax.plot(drift_data['lon'][k,:idx],drift_data['lat'][k,:idx],linewidth = .2,color=area_colors[mask_i-1])
               


    # add lines at boundaries
    ax.plot([-11, -1.1], [48.5, 48.5], linestyle=':',color='black',linewidth=0.5)
    ax.plot([-11, -1.1], [41, 41], linestyle=':',color='black',linewidth=0.5)
    ax.plot([-11, -11], [38.95, 50.5], linestyle=':',color='black',linewidth=0.5)
    
    # Define two levels: sea (<=0) and land (>0) 
    levels = [-1e9, 0, 1e9] # anything below 0, and anything above 0 
    # Colors: ocean = transparent or blue, land = white 
    colors = ['none', 'white'] # or ['lightblue', 'white'] 
    ax.contourf(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'], levels=levels, colors=colors,zorder=10)
    ax.contour(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'],levels=bathy_levels,colors='black',linewidths=0.5) 
    ax.contour(bathy_data['lon'],bathy_data['lat'],bathy_data['depth'],levels=[0],colors='black',linewidths=0.5,zorder=11)

    # Add grid and title
    # ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)
    #time1 = drift_data['time'][10].strftime("%m-%Y")
    #ax.set_title(f'Trajectories of particles seeded in {time1}; {age} days', fontsize=8)
          
    #ax.set_xlabel('longitude')
    #ax.set_ylabel('latitude')
    ax.set_xticks([-12,-10,-8,-6,-4,-2])
    
    plt.rcParams.update({
        "font.size": 9,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8
    })
        

    return ax



# ==========================================
# ---- Do the plotting here -------
# ===========================================


# load bathymetry files
bathy_data = read_bathymetry(bathy_file)



fig, axs = plt.subplots(1, 3, figsize=(6.8,4.1), sharex=True, sharey=True)


# first subplot
yr = 2015
mo = 11
sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
drift_data = read_driftdata(sim_file)
ax=axs[0]
ax = plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,masks_to_plot)
ax.set_xlabel('longitude')
ax.set_ylabel('latitude')
ax.text(-12.5,50,'(a)')


# second subplot
yr = 2016
mo = 2
sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
drift_data = read_driftdata(sim_file)
ax=axs[1]
ax = plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,masks_to_plot)
ax.set_xlabel('longitude')
ax.set_ylabel('')
ax.text(-12.5,50,'(b)')

# second subplot
yr = 2021
mo = 5
sim_file = f'{sim_folder}/Connectivity_backward_{yr}_{mo:02d}.nc'
drift_data = read_driftdata(sim_file)
ax=axs[2]
ax = plot_trajectory_origen_age(drift_data,bathy_data,area_colors,area_labels,bathy_levels,age,ax,masks_to_plot)
ax.set_xlabel('longitude')
ax.set_ylabel('')
ax.text(-12.5,50,'(c)')

patches = [Patch(color=area_colors[i-1], label=area_labels[i-1]) for i in masks_to_plot]
ax.legend(handles=patches, loc='lower right',fontsize=6)     


# save figure
fig.tight_layout()
fig.savefig(f'{plot_folder}/Figure_2_Trajectory_particles_origin.png',dpi=300,bbox_inches="tight")










