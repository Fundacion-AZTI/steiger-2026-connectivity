#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 11:26:55 2026

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


# input to be changed by user
yr = [2016,2021,2015]
mo = [2]
age = 90
masks_to_plot = [8,2,3,4,5,6,7,1]


# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
result_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/travel_time/'

# -- general settings-----
area_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
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
def plot_time_since_left_area(lon,lat,var,bathy_data,bathy_levels,clim_max,Ncolors,ax,fig):
    
    lon0 = [-11, -1]
    lat0 = [41, 48.5]
    
    
    cmap = colormaps['viridis'].resampled(Ncolors)
    sc = ax.scatter(lon, lat, s=9, c=var, cmap=cmap, vmin=0, vmax=clim_max)
 
    
    # Plot bathymetry contours
    ax.contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)

    # Add grid and title
    #ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)

    ax.set_xlim(min(lon0), max(lon0))
    ax.set_ylim(min(lat0), max(lat0))
    
    # Add colorbar inside the subplot (bottom-right corner)
    cax = inset_axes(axs[-1,-1], width="40%", height="4%", loc='lower right',
                     borderpad=4)  # loc can be 'upper right', 'lower left', etc.
    cb = fig.colorbar(sc, cax=cax, orientation='horizontal')
    #cb.set_ticks([7, 30, 90])
    #cb.set_ticklabels(["7", "30", "90"])
    cax.tick_params(labelsize=6)


    return ax, sc, cb


# In[3]
# ==========================================
# ---- FIGURE 5 - MEAN TRAVEL TIMES -------
# ===========================================

area_numbers = [1,2,3,4,5,6,7,8]
cmax = 91
cont_levels=[25,50,75,90]
lon0 = [-11, -1]
lat0 = [41, 48.5]
txt = ['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)']

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

# statistics was created in "analyse_travel_time.py" 
df_stats = pd.read_csv(f'{result_folder}/time_area_lonlat_stats.csv')


# --- FIGURE of the MEAN TRAVEL IME at each seeding position ----
fig, axs = plt.subplots(2, 4, figsize=(6.8,4.1), sharex=True, sharey=True)


for cnt, a in enumerate(area_numbers):
    i,j = ((a-1) // 4, (a-1) % 4)
    lon = df_stats[df_stats['area']==a]['lon']
    lat = df_stats[df_stats['area']==a]['lat']
    mean = df_stats[df_stats['area']==a]['time_mean']
    mean[mean>90]=np.nan
    count = 100-df_stats[df_stats['area']==a]['count']/df_stats[df_stats['area']==a]['count'].max()*100

    # create count within a gridded lon/lat for contour plot
    lon_bins = np.linspace(lon.min(), lon.max() + 1e-6, 80)
    lat_bins = np.linspace(lat.min(), lat.max() + 1e-6, 80)
    Lon, Lat = np.meshgrid(lon_bins, lat_bins)
    lon_centers = 0.5 * (lon_bins[:-1] + lon_bins[1:])
    lat_centers = 0.5 * (lat_bins[:-1] + lat_bins[1:])

    count_grid, _, _ = np.histogram2d(lat, lon, bins=[lat_bins, lon_bins], weights=count)
    hits, _, _       = np.histogram2d(lat, lon, bins=[lat_bins, lon_bins])

    count_mean = count_grid/ hits
    count_mean[hits == 0] = np.nan

    # create colormap
    cmap = make_segmented_concat_cmap(cmax)
    
    
    # Plot ocean in grey
    ocean_mask = (bathy_data['depth'] < 0)
    axs[i,j].pcolormesh(bathy_data['lon'], bathy_data['lat'], ocean_mask, cmap=plt.cm.Greys, shading="auto", alpha=0.3)

    
    # make scatter plots
    sc = axs[i,j].scatter(lon, lat, s=9, c=mean, cmap=cmap, vmin=0, vmax=cmax)
 
    # Plot contours for particles counts included in the calculation of the mean
    cs = axs[i,j].contour(lon_centers,lat_centers, count_mean, levels=cont_levels, colors='black', linewidths=1)
    
    axs[i,j].clabel(cs, inline=True, fontsize=8)

    # Plot bathymetry contours
    axs[i,j].contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)
   

    # Add grid and title
    #ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)
    axs[i,j].set_xlim(min(lon0), max(lon0))
    axs[i,j].set_ylim(min(lat0), max(lat0))
    axs[i,j].set_xticks([-10,-8,-6,-4,-2])
    
    #ax[i,j].set_title(area_labels[a-1])
    if i==1:
        axs[i,j].set_xlabel('Longitude')
    if j==0:
        axs[i,j].set_ylabel('Latitude')
        
    
    axs[i,j].text(-2.5,47.8,txt[cnt])
  


# # Add colorbar inside the last subplot (bottom-right corner)
cax = inset_axes(axs[-1,-1], width="50%", height="5%", loc='lower right', bbox_to_anchor=(-0.05, 0.2, 1, 1),
                 bbox_transform=axs[-1,-1].transAxes,borderpad=0)  # loc can be 'upper right', 'lower left', etc.
cb = fig.colorbar(sc, cax=cax, orientation='horizontal')
cb.set_label('time (days)',labelpad=-1)
cb.set_ticks([7, 30, 90])
cb.set_ticklabels(["7", "30", "90"])

        
plt.rcParams.update({
     "font.size": 9,
     "axes.labelsize": 9,
     "xtick.labelsize": 8,
     "ytick.labelsize": 8
})

              
plt.tight_layout()
fig.savefig(f'{plot_folder}/Figure_5_Travel_time_mean_area_all.png',dpi=300, bbox_inches='tight', pad_inches=0)



# In[4]
# ==========================================
# ---- FIGURE 16 - STD of TRAVEL TIME -------
# ===========================================

area_numbers = [1,2,3,4,5,6,7,8]
cmax = 91
cont_levels=[25,50,75,90]
lon0 = [-11, -1]
lat0 = [41, 48.5]

cmax = 35
Ncolors = 7

txt = ['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)']

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

# statistics was created in "analyse_travel_time.py" 
df_stats = pd.read_csv(f'{result_folder}/time_area_lonlat_stats.csv')


# --- FIGURE of the MEAN TRAVEL IME at each seeding position ----
fig, axs = plt.subplots(2, 4, figsize=(6.8,4.1), sharex=True, sharey=True)

for cnt, a in enumerate(area_numbers):
    i,j = ((a-1) // 4, (a-1) % 4)
    lon = df_stats[df_stats['area']==a]['lon']
    lat = df_stats[df_stats['area']==a]['lat']
    mean = df_stats[df_stats['area']==a]['time_mean']
    std = df_stats[df_stats['area']==a]['time_std']
    std[mean>90]=np.nan

    
    cmap = colormaps['viridis'].resampled(Ncolors)
    
    # Plot ocean in grey
    ocean_mask = (bathy_data['depth'] < 0)
    axs[i,j].pcolormesh(bathy_data['lon'], bathy_data['lat'], ocean_mask, cmap=plt.cm.Greys, shading="auto", alpha=0.3)

    # make scatter plot
    sc = axs[i,j].scatter(lon, lat, s=9, c=std, cmap=cmap, vmin=0, vmax=cmax)
 
    
    # Plot bathymetry contours
    axs[i,j].contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)

    # Add grid and title
    #ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)

    axs[i,j].set_xlim(min(lon0), max(lon0))
    axs[i,j].set_ylim(min(lat0), max(lat0))
    axs[i,j].set_xticks([-10,-8,-6,-4,-2])
    
    axs[i,j].text(-2.5,47.8,txt[cnt])

    #axs[i,j].set_title(area_labels[a-1])
    if i==1:
        axs[i,j].set_xlabel('Longitude')
    if j==0:
        axs[i,j].set_ylabel('Latitude')  


cax = inset_axes(axs[-1,-1], width="50%", height="5%", loc='lower right', bbox_to_anchor=(-0.05, 0.2, 1, 1),
                 bbox_transform=axs[i,j].transAxes,borderpad=0)  # loc can be 'upper right', 'lower left', etc.
cb = fig.colorbar(sc, cax=cax, orientation='horizontal')
cb.set_label('std (days)',labelpad=-1)   
cb.set_ticks([0,10,20,30])
#cb.set_ticklabels(["7", "30", "90"])
        
plt.rcParams.update({
     "font.size": 9,
     "axes.labelsize": 9,
     "xtick.labelsize": 8,
     "ytick.labelsize": 8
})

              
plt.tight_layout()
fig.savefig(f'{plot_folder}/Figure_16_Travel_time_std_area_all.png',dpi=300, bbox_inches='tight', pad_inches=0)


