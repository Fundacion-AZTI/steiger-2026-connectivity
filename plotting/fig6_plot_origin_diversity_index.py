#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jul 14 13:53:10 2026

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
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
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



def plot_mixing_heat_map(mixing_index,lat_bins,lon_bins,bathy_data,bathy_levels,ax,fig):

    
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



    # Plot bathymetry contours
    ax.contour(bathy_data['lon'], bathy_data['lat'], bathy_data['depth'], levels=bathy_levels, colors='black', linewidths=0.5)

    # Add grid and title
    #ax.grid(which='both', axis='both', color='gray', linestyle='--', linewidth=0.5)
    ax.set_xlabel('Longitude')
    ax.set_ylabel('Latitude')
    ax.set_xticks([-12,-10,-8,-6,-4,-2])

    
    if fig is None:
        return ax, fig, pcm
        plt.show()
    else:
        return ax, pcm
    


# In[3]
# Plot Climatologies of mixing index for 7, 30, 90 days
# READ mixing_index and plot as heatmap for climatologies

create_figure = None
mos=[2,5,8,11]
yrs=np.arange(1994,2025)

# load bathymetry files
bathy_data = read_bathymetry(bathy_file)

# --- Prepare figure ---
fig, axs = plt.subplots(len(mos), 3, figsize=(6.8,10.2), sharex=True, sharey=True)

lat_bins = None
lon_bins = None

mix7  = [[] for _ in mos]   # one list per month
mix30 = [[] for _ in mos]
mix90 = [[] for _ in mos]

txt = ['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)','(i)','(j)','(k)','(l)']

# --- Load only requested months ---
for yr in yrs:

    ds7  = xr.load_dataset(f"{res_folder}/mixing_7_{yr}.nc")
    ds30 = xr.load_dataset(f"{res_folder}/mixing_30_{yr}.nc")
    ds90 = xr.load_dataset(f"{res_folder}/mixing_90_{yr}.nc")

    if lat_bins is None:
        lat_bins = ds7.lat_bins.values
        lon_bins = ds7.lon_bins.values

    # Loop through your target months
    for idx, mo in enumerate(mos):

        # Extract the correct month index inside the file:
        # ds7.month is usually an array [1..12]; find the index of mo
        month_index7 = int(np.where(ds7.month.values == mo)[0])
        month_index30 = int(np.where(ds30.month.values == mo)[0])
        month_index90 = int(np.where(ds90.month.values == mo)[0])
        
        mix7[idx].append( ds7.mixing.isel(month=month_index7) )
        mix30[idx].append(ds30.mixing.isel(month=month_index30))
        mix90[idx].append(ds90.mixing.isel(month=month_index90))



# --- Plotting ---
for i, mo in enumerate(mos):

    mixing_mean_7  = compute_monthly_mean(mix7[i])
    mixing_mean_30 = compute_monthly_mean(mix30[i])
    mixing_mean_90 = compute_monthly_mean(mix90[i])

    # first column: 7 days
    ax, pcm = plot_mixing_heat_map(mixing_mean_7, lat_bins, lon_bins,bathy_data, bathy_levels, axs[i,0], fig)
    ax.text(-12.5,49.5,txt[i*3])
    if mo<mos[-1]:
        axs[i,0].set_xlabel('')

    #second column: 30 days
    ax, pcm = plot_mixing_heat_map(mixing_mean_30, lat_bins, lon_bins,bathy_data, bathy_levels, axs[i,1], fig)
    #axs[i,1].set_title(f"Month {mo:02d}; 30 days")
    axs[i,1].set_ylabel('')
    ax.text(-12.5,49.5,txt[i*3+1])
    if mo<mos[-1]:
         axs[i,1].set_xlabel('')

    #third column: 90 days
    ax, pcm = plot_mixing_heat_map(mixing_mean_90, lat_bins, lon_bins,bathy_data, bathy_levels, axs[i,2], fig)
    #axs[i,2].set_title(f"Month {mo:02d}; 90 days")
    axs[i,2].set_ylabel('')
    ax.text(-12.5,49.5,txt[i*3+2])
    if mo<mos[-1]:
        axs[i,2].set_xlabel('')

# Add colorbar inside the subplot (bottom-right corner)
cax = inset_axes(axs[-1,-1], width="50%", height="5%", loc='lower right',bbox_to_anchor=(-0.05, 0.15, 1, 1),
                 bbox_transform=axs[-1,-1].transAxes,borderpad=0)  # loc can be 'upper right', 'lower left', etc.
fig.colorbar(pcm, cax=cax, ticks=np.arange(0, 9), orientation='horizontal')
cax.set_title('ODI')
    

plt.rcParams.update({
     "font.size": 9,
     "axes.labelsize": 9,
     "xtick.labelsize": 8,
     "ytick.labelsize": 8
})

              
plt.tight_layout()
fig.savefig(f'{plot_folder}/Figure_6_Origin_diversity_index.png',dpi=300, bbox_inches='tight')
 