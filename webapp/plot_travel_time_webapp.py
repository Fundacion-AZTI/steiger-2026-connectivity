#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 16:29:10 2026

@author: nsteiger
"""

# In[1]

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
import netCDF4 as nc
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib import colormaps
import pandas as pd



# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/webapp/figures/travel_time/'
result_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/travel_time/'

# -- general settings-----
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]


# In[2]
# Prepare functions

# ---- function to read bathymetry data ------
def read_bathymetry(bathy_file):
    bathy_data = nc.Dataset(bathy_file, model='r')
    return {
        'lon': bathy_data.variables['lon'][:],
        'lat': bathy_data.variables['lat'][:],
        'depth': bathy_data.variables['elevation'][:]
    }

# function to create colormap 
def make_segmented_concat_cmap(clim_max):

    # base colormaps
    cmaps = [
        colormaps["Blues_r"],
        colormaps["Greens_r"],
        colormaps["Oranges_r"],
        colormaps["Greys_r"]
    ]

    # number of samples per segment (can be tuned)
    Ns = [8,23,60, clim_max-90]


    # sample and concatenate
    colors = []
    for cmap, N in zip(cmaps, Ns):
        colors.append(cmap(np.linspace(0.1, 0.9, N)))   # sample the gradient

    colors = np.vstack(colors)

    # Build a fully continuous colormap from the sampled colors
    full_cmap = LinearSegmentedColormap.from_list("concat_timesince", colors)

    return full_cmap


# plotting function for mean travel time and std
def plot_time_since_left_area(lon,lat,var,bathy_data,bathy_levels,clim_max):
    
    fig, ax = plt.subplots(figsize=(5,6.2))
    
    lon0 = [-11, -1]
    lat0 = [41, 48.5]
    
    # create colormap
    cmap = make_segmented_concat_cmap(clim_max)
    
    # Plot ocean in grey
    ocean_mask = (bathy_data['depth'] < 0)
    ax.pcolormesh(bathy_data['lon'], bathy_data['lat'], ocean_mask, cmap=plt.cm.Greys, shading="auto", alpha=0.3)

    
    # make scatter plots
    sc = ax.scatter(lon, lat, s=5, c=var, cmap=cmap, vmin=0, vmax=clim_max)
 
    
    # Plot bathymetry contours
    ax.contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)

 
    ax.set_xlim(min(lon0), max(lon0))
    ax.set_ylim(min(lat0), max(lat0))
    ax.set_xticks([-10,-8,-6,-4,-2])
    
    # Add colorbar inside the subplot (bottom-right corner)
    cax = inset_axes(ax, width="40%", height="4%", loc='lower right',
                     borderpad=4)  # loc can be 'upper right', 'lower left', etc.
    cb = fig.colorbar(sc, cax=cax, orientation='horizontal')
    cb.set_ticks([7, 30, 90])
    cb.set_ticklabels(["7", "30", "90"])
    cb.set_label('time (days)',labelpad=0)

    
 
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
        
    

    plt.rcParams.update({
         "font.size": 9,
         "axes.labelsize": 9,
         "xtick.labelsize": 8,
         "ytick.labelsize": 8
    })


    return fig, ax, sc, cb



# In[3]
# MONTHLY PLOTS

area_numbers = [1,2,3,4,5,6,7,8]
cmax = 91

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)


    
    
mos = np.arange(1,13)
yrs = np.arange(1994, 2025)

for i, mo in enumerate(mos):
    for j, yr in enumerate(yrs):
        
        # Read only the parquet file for the selected year/month
        time_month = pd.read_parquet(f"{result_folder}/Travel_time_from_area_to_seeding_{yr}_{mo:02d}.parquet")
        
        for a in area_numbers:
            time_area = time_month[time_month['area']==a]
            time_mean = (
                time_area
                .groupby(['lon', 'lat'], as_index=False)['time']
                .mean()
            )
        
            lon = time_mean['lon']
            lat = time_mean['lat']
            var = time_mean['time']
            var[var > 90] = np.nan
        
            fig, ax, sc, cb = plot_time_since_left_area(lon, lat, var,bathy_data, bathy_levels, cmax)
            
            ax.set_title(f'Travel time from {area_labels[a-1]} for particles seeded during {mo:02d}/{yr}')
        
            plt.tight_layout()

            fig.savefig(f'{plot_folder}/Travel_time_{yr}_{mo:02d}_{area_labels[a-1]}.png', dpi=300, bbox_inches='tight', pad_inches=0)
            plt.close(fig)
            
            
            
            
            
# In[4]
# CLIMATOLOGY (ONE FOR EACH MONTH)

area_numbers = [1,2,3,4,5,6,7,8]
cmax = 91

months =['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)



mos = np.arange(1,13)
yrs = np.arange(1994, 2025)

for i, mo in enumerate(mos):
    time_month = pd.concat([
        pd.read_parquet(f"{result_folder}/Travel_time_from_area_to_seeding_{yr}_{mo:02d}.parquet") for yr in yrs],
        ignore_index=True)   # concatenate all years to calculate monthly climatology
        
    for a in area_numbers:
        time_area = time_month[time_month['area']==a]
        time_mean = (
            time_area
            .groupby(['lon', 'lat'], as_index=False)['time']
            .mean()
        )
    
        lon = time_mean['lon']
        lat = time_mean['lat']
        var = time_mean['time']
        var[var > 90] = np.nan
    
        fig, ax, sc, cb = plot_time_since_left_area(lon, lat, var,bathy_data, bathy_levels, cmax)
    
        ax.set_title(f'Mean travel time from {area_labels[a-1]} for particles seeded during {months[i]}')
        plt.tight_layout()

        fig.savefig(f'{plot_folder}/Travel_time_mean_{mo:02d}_{area_labels[a-1]}.png', dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close(fig)
        
        
        
        
# In[5]
# YEARLY MEAN

area_numbers = [1,2,3,4,5,6,7,8]
cmax = 91

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)



mos = np.arange(1,13)
yrs = np.arange(1994, 2025)

for i, yr in enumerate(yrs):
    time_month = pd.concat([
        pd.read_parquet(f"{result_folder}/Travel_time_from_area_to_seeding_{yr}_{mo:02d}.parquet") for mo in mos],
        ignore_index=True)   # concatenate all months to calculate yearly mean
        
    for a in area_numbers:
        time_area = time_month[time_month['area']==a]
        time_mean = (
            time_area
            .groupby(['lon', 'lat'], as_index=False)['time']
            .mean()
        )
    
        lon = time_mean['lon']
        lat = time_mean['lat']
        var = time_mean['time']
        var[var > 90] = np.nan
    
        fig, ax, sc, cb = plot_time_since_left_area(lon, lat, var,bathy_data, bathy_levels, cmax)
    
        ax.set_title(f'Mean travel time from {area_labels[a-1]} for particles seeded during {yr}')
        plt.tight_layout()

        fig.savefig(f'{plot_folder}/Travel_time_{yr}_mean_{area_labels[a-1]}.png', dpi=300, bbox_inches='tight', pad_inches=0)
        plt.close(fig)        
        
        
        
        
# In[6]
# TOTAL MEAN

area_numbers = [1,2,3,4,5,6,7,8]
cmax = 91

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)



mos = np.arange(1,13)
yrs = np.arange(1994, 2025)


time_all = pd.concat([
        pd.read_parquet(f"{result_folder}/Travel_time_from_area_to_seeding_{yr}_{mo:02d}.parquet")
        for yr in yrs
        for mo in mos],ignore_index=True)
        
for a in area_numbers:
    time_area = time_all[time_all['area']==a]
    time_mean = (
        time_area
        .groupby(['lon', 'lat'], as_index=False)['time']
        .mean()
    )

    lon = time_mean['lon']
    lat = time_mean['lat']
    var = time_mean['time']
    var[var > 90] = np.nan

    fig, ax, sc, cb = plot_time_since_left_area(lon, lat, var,bathy_data, bathy_levels, cmax)

    ax.set_title(f'Mean travel time for particles from {area_labels[a-1]}')
    plt.tight_layout()

    fig.savefig(f'{plot_folder}/Travel_time_mean_mean_{area_labels[a-1]}.png', dpi=300, bbox_inches='tight', pad_inches=0)
    plt.close(fig)        