#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 18 13:20:20 2026

@author: nsteiger
"""

# In[1]

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import netCDF4 as nc
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.colors import ListedColormap
from matplotlib import colormaps

# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/webapp/figures/ODI/'
res_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/mixing/'

# -- general settings-----
area_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]




# In[2]
# define functions

# --- Monthly mean function (now simple!) ---
def compute_monthly_mean(mix_list):
    # mix_list already contains only the desired months
    arrs = [arr.values for arr in mix_list]
    return np.nanmean(np.stack(arrs), axis=0)



# ---- function to read bathymetry data ------
def read_bathymetry(bathy_file):
    bathy_data = nc.Dataset(bathy_file, model='r')
    return {
        'lon': bathy_data.variables['lon'][:],
        'lat': bathy_data.variables['lat'][:],
        'depth': bathy_data.variables['elevation'][:]
    }



def plot_mixing_heat_map(mixing_index,lat_bins,lon_bins,bathy_data,bathy_levels):

    fig = plt.figure(figsize=(5, 6.2))
    ax = plt.gca()
    
    # Ensure mixing_index is float for NaNs
    mixing_index = mixing_index.astype(float)
    
    vmin = -0.5
    vmax = 6.5
    #cmap = plt.get_cmap('afmhot_r',vmax-vmin)
    viridis = colormaps['viridis_r'].resampled(6)
    colors = viridis(np.arange(6))
    
    # prepend white
    colors = np.vstack(([1, 1, 1, 1], colors))
    
    cmap = ListedColormap(colors)

        
    # Plot heatmap
    pcm = ax.imshow(mixing_index, origin='lower',
               extent=[lon_bins[0], lon_bins[-1], lat_bins[0], lat_bins[-1]],
               cmap=cmap, aspect='auto', vmin=vmin, vmax=vmax)
    
#    cbar = fig.colorbar(pcm, ax=axs, orientation='horizontal', fraction=0.02, pad=0.02)
#    cbar.set_label('Number of Unique Origins')

    # Add colorbar in bottom-right corner
    cax = inset_axes(ax, width="50%", height="5%", loc='lower right',bbox_to_anchor=(-0.05, 0.15, 1, 1),
                     bbox_transform=ax.transAxes,borderpad=0)  # loc can be 'upper right', 'lower left', etc.
    fig.colorbar(pcm, cax=cax, ticks=np.arange(0, 9), orientation='horizontal')
    cax.set_title('ODI')

    # Plot bathymetry contours
    ax.contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)

    # Add grid and title
    #ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xticks([-12,-10,-8,-6,-4,-2])

    plt.rcParams.update({
         "font.size": 9,
         "axes.labelsize": 9,
         "xtick.labelsize": 8,
         "ytick.labelsize": 8
    })

    return ax, fig, pcm




# In[3]
# Plot Monthly maps of mixing index for 7, 30, 90 days
# READ mixing_index and plot as heatmap for climatologies

mos=np.arange(1,13)
yrs=np.arange(2004,2025)
ages = [90]  # still 30 and 90 to do!!!!


# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

# --- Prepare figure ---
lat_bins = None
lon_bins = None


for age in ages:
    # --- Loop over all monhts and years ---
    for yr in yrs:
    
        ds  = xr.load_dataset(f"{res_folder}/mixing_{age}_{yr}.nc")
    
        if lat_bins is None:
            lat_bins = ds.lat_bins.values
            lon_bins = ds.lon_bins.values
    
        # Loop through your target months
        for idx, mo in enumerate(mos):
    
            # Extract the correct month index inside the file:
            # ds7.month is usually an array [1..12]; find the index of mo
            month_index = int(np.where(ds.month.values == mo)[0])
    
            mix = ds.mixing.isel(month=month_index)
            # mix30[idx].append(ds30.mixing.isel(month=month_index))
            # mix90[idx].append(ds90.mixing.isel(month=month_index))
    
    
            # --- Plotting ---
            # mixing_mean_7  = compute_monthly_mean(mix7[i])
            # mixing_mean_30 = compute_monthly_mean(mix30[i])
            # mixing_mean_90 = compute_monthly_mean(mix90[i])
        
            ax, fig, pcm = plot_mixing_heat_map(mix, lat_bins, lon_bins,bathy_data, bathy_levels)
    
            ax.set_title(f'Origin diversity index for particles seeded in {mo:02d}/{yr}')
                  
            plt.tight_layout()
            fig.savefig(f'{plot_folder}/ODI_{age:02d}_{yr}_{mo:02d}.png',dpi=300, bbox_inches='tight')


# In[4]
# ====== MONTHLY Climatology ===================
# --- Prepare figure ---
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
lat_bins = None
lon_bins = None

mos=np.arange(1,13)
yrs=np.arange(1994,2025)
ages = [7,30,90]  

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

for age in ages:
    mix  = [[] for _ in mos]   # one list per month
    # --- Loop over all monhts and years ---
    for yr in yrs:
    
        ds  = xr.load_dataset(f"{res_folder}/mixing_{age}_{yr}.nc")
    
        if lat_bins is None:
            lat_bins = ds.lat_bins.values
            lon_bins = ds.lon_bins.values
    
        # Loop through your target months
        for idx, mo in enumerate(mos):
    
            # Extract the correct month index inside the file:
            # ds7.month is usually an array [1..12]; find the index of mo
            month_index = int(np.where(ds.month.values == mo)[0])
    
            mix[idx].append(ds.mixing.isel(month=month_index))
    
    
    # --- Plotting ---
    for idx, mo in enumerate(mos):
        mixing_mean  = compute_monthly_mean(mix[idx])
    
    
        # first column: 7 days
        ax, fig, pcm = plot_mixing_heat_map(mixing_mean, lat_bins, lon_bins,bathy_data, bathy_levels)
    
        ax.set_title(f'Mean origin diversity index for particles seeded in {months[idx]}')
              
        plt.tight_layout()
        fig.savefig(f'{plot_folder}/ODI_{age:02d}_mean_{mo:02d}.png',dpi=300, bbox_inches='tight')


# In[5]
# ====== Yearly MEAN ===================
# --- Prepare figure ---
lat_bins = None
lon_bins = None


mos=np.arange(1,13)
yrs=np.arange(1994,2025)
ages = [7,30,90] 

for age in ages:
    # --- Loop over all monhts and years ---
    for yr in yrs:
    
        ds  = xr.load_dataset(f"{res_folder}/mixing_{age}_{yr}.nc")
    
        if lat_bins is None:
            lat_bins = ds.lat_bins.values
            lon_bins = ds.lon_bins.values
    

        mixing_mean = ds['mixing'].mean(dim='month').values
    
    
        # first column: 7 days
        ax, fig, pcm = plot_mixing_heat_map(mixing_mean, lat_bins, lon_bins,bathy_data, bathy_levels)
    
        ax.set_title(f'Mean origin diversity index for particles seeded in {yr}')
              
        plt.tight_layout()
        fig.savefig(f'{plot_folder}/ODI_{age:02d}_{yr}_mean.png',dpi=300, bbox_inches='tight')
        
        
        
        
# In[6]
# ====== MONTHLY ALL ===================
# --- Prepare figure ---
lat_bins = None
lon_bins = None

mos=np.arange(1,13)
yrs=np.arange(1994,2025)
ages = [7,30,90]  



for age in ages:
    ds_all  = []   # one list 
    # --- Loop over all monhts and years ---
    for yr in yrs:
    
        ds  = xr.load_dataset(f"{res_folder}/mixing_{age}_{yr}.nc")
    
        if lat_bins is None:
            lat_bins = ds.lat_bins.values
            lon_bins = ds.lon_bins.values

    
        ds_all.append(ds.mixing.expand_dims(year=[yr]))
    
    
    # --- Plotting ---

    # concatenate all years
    mixing_all = xr.concat(ds_all, dim="year")

    mixing_mean = mixing_all.mean(dim=["year","month"])


    # first column: 7 days
    ax, fig, pcm = plot_mixing_heat_map(mixing_mean, lat_bins, lon_bins,bathy_data, bathy_levels)

    ax.set_title('Mean origin diversity index over 1994-2024')
          
    plt.tight_layout()
    fig.savefig(f'{plot_folder}/ODI_{age:02d}_mean_mean.png',dpi=300, bbox_inches='tight')