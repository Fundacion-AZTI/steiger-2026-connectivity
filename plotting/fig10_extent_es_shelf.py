#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 15:34:27 2026

@author: nsteiger
"""

# In[1]
# This section is needed for all sections below - run it first
# following sections can be executed independently

# load necessary functions
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import linregress
import xarray as xr
import calendar
import matplotlib.gridspec as gridspec

# --- paths ----
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
results_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/origin/'


# -- general settings-----
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]



# -- needed functions--------

def two_modes(col):
    vals, counts = np.unique(col,return_counts=True)
    order = np.argsort(-counts)
    first = vals[order[0]]
    second = vals[order[1]] if len(order) > 1 else np.nan
    return first, second


# In[4]
# Plot max latitude ANOMALY of es_shelf water as Hovmoller of month and year



mos = np.arange(1,13)
yrs = np.arange(1994, 2025)
age = 90
orig = 5
perc = 99.9

# --- Prepare the Hovmöller grid: shape (n_months, n_years) ---
M = len(mos)
Y = len(yrs)
H = np.full((M, Y), np.nan)  # will hold the 99.5th percentile latitude per (month, year)
lat_max_ipc = []

for iy, yr in enumerate(yrs):
    origin_file = f'{results_folder}/Lon_Lat_Origin_{yr}_year.nc'
    ds = xr.open_dataset(origin_file, decode_times=True)

    for im, mo in enumerate(mos):
        # Select month
        ds_mo = ds.where(ds['month'] == mo, drop=True)

        # Pull arrays; use .values and ravel to ensure flat arrays for boolean indexing
        lat_ini     = np.asarray(ds_mo['lat_00'].values).ravel()
        origin_age  = np.asarray(ds_mo[f'origin_{age:02d}'].values).ravel()

        # Filter by origin and compute the 99.5th percentile if we have data
        lat_orig = lat_ini[origin_age == orig]
        if lat_orig.size > 0:
            H[im, iy] = np.percentile(lat_orig, perc)
        else:
            H[im, iy] = np.nan  # keep NaN for missing data
        lat_max_ipc.append(np.percentile(lat_orig, perc))   
        

# calculate seasonal cycle
H_monthly_clim = np.nanmean(H, axis=1)   # shape = (12,)
H_monthly_std = np.nanstd(H, axis=1)   # shape = (12,)
H_clim_2d = np.tile(H_monthly_clim[:, None], (1, H.shape[1]))
H_anom = H - H_clim_2d

# calculate yearly anomalies
H_yearly_anom = np.nanmean(H_anom, axis=0) 
H_yearly_std = np.nanstd(H_anom, axis=0) 

# --------------------------
# --- Plot the Hovmöller ---
# --------------------------


fig = plt.figure(figsize=(6.8,3.4))

# GridSpec: 2 rows, 2 columns
# Row 0: only one panel across both columns
# Row 1: narrow left (seasonal cycle) + wide right (Hovmöller)
gs = gridspec.GridSpec(
    2, 2,
    height_ratios=[1.2, 4],      # top row is smaller
    width_ratios=[0.6, 4],    # left column is very narrow
    hspace=0.1,
    wspace=0.05
)

x = np.arange(Y)
y = np.arange(M)

# -----------------------------------------------
# (A) Top panel — Yearly anomaly time series
# -----------------------------------------------
ax_top = fig.add_subplot(gs[0, 1])    

ax_top.plot(x, H_yearly_anom, marker='o', color='black', markersize=2)
ax_top.fill_between(
    x,
    H_yearly_anom - H_yearly_std,
    H_yearly_anom + H_yearly_std,
    color='gray', edgecolor='none',
    alpha=0.3,
    label='±1 std'
)
ax_top.axhline(0, color='gray', linewidth=0.8)

ax_top.set_ylabel("Latitude\nanom. [°N]")
#ax_top.set_title(f"Yearly-averaged anomalies of max latitude of {area_labels[orig-1]} water ({age} days)")

# Share x-axis with the Hovmöller → ticks only on bottom panel
ax_top.set_xticks(np.arange(Y))
ax_top.set_xticklabels([])
ax_top.text(0.5,0.6,'(a)')

# --------------------
# (B) LEFT panel: Seasonal cycle (narrow)
# --------------------
ax_left = fig.add_subplot(gs[1,0])

ax_left.plot(H_monthly_clim, y, marker='o', color='black',markersize=2)
ax_left.fill_betweenx(
    y,
    H_monthly_clim - H_monthly_std,
    H_monthly_clim + H_monthly_std,
    color='gray', edgecolor='none',
    alpha=0.3,
    label='±1 std'
)

ax_left.set_xticks([46,47,48])
ax_left.set_ylim(M-0.5, -0.5)  # match Hovmöller orientation

# Month ticks on left panel
ax_left.set_yticks(np.arange(M))
ax_left.set_yticklabels([calendar.month_abbr[m][0] for m in mos])

ax_left.set_xlabel('Latitude [°N]')
#ax_left.set_title('Seasonal cycle')
ax_left.text(46.3,1,'(b)')

# Add a box around this axis
for spine in ax_left.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.1)

# --------------------
# (C) RIGHT panel: Hovmöller anomaly
# --------------------
ax_hov = fig.add_subplot(gs[1,1])

data_anom = np.ma.masked_invalid(H_anom)
cmap = plt.get_cmap('RdBu_r').copy()
cmap.set_bad(color='lightgray')

mesh = ax_hov.pcolormesh(x, y, data_anom, cmap=cmap, shading='nearest')


# --- Compute trend + significance ---
lat_max_ipc = np.array(lat_max_ipc)   # shape = (Y*M,)

# Build a month index array: 0..11 repeating
month_idx = np.tile(np.arange(12), len(yrs))

# Compute anomalies
lat_max_anom = lat_max_ipc - H_monthly_clim[month_idx]

t = np.arange(len(lat_max_anom))
slope, intercept, r_value, p_value, stderr = linregress(t, lat_max_anom)

# Add the trend text to the plot
plt.text(
    0.05, 0.2,
    f"trend = {slope:.4f} [°N] month$^{{-1}}$\npval = {p_value:.3g}",
    transform=ax_hov.transAxes,
    verticalalignment="top",
)

ax_hov.set_xticks(np.arange(Y))
ax_hov.set_xticklabels([str(yy) for yy in yrs], rotation=90)

# Month labels on left panel only → so hide these
ax_hov.set_yticks(np.arange(M))
ax_hov.set_yticklabels([])

ax_hov.set_xlabel('Year')
ax_hov.invert_yaxis()

ax_hov.text(0.5,1,'(c)')

# Optional: set color scale limits if you want consistent scaling
vmin, vmax = -1.2, 1.2
mesh.set_clim(vmin=vmin, vmax=vmax)
cbar = fig.colorbar(mesh, ax=ax_hov, pad=0.02)
cbar.set_label('Latitude anomaly [°N]')



# --- MATCH ax_top WIDTH TO ax_hov WIDTH ---
# Get pixel bounds of the Hovmöller axis
hov_pos = ax_hov.get_position()
top_pos = ax_top.get_position()
ax_top.set_position([
    hov_pos.x0,
    top_pos.y0,
    hov_pos.width,
    top_pos.height
])


ax_top.set_xlim(ax_hov.get_xlim())
ax_top.margins(x=0)


plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8
})

plt.show()
fig.tight_layout()


fig.savefig(f'{plot_folder}/Figure_10_Northward_extent.png',bbox_inches='tight')






# In[4]
# Plot max latitude ANOMALY of es_shelf water as Hovmoller of month and year



mos = np.arange(1,13)
yrs = np.arange(1994, 2025)
age = 90
orig = 5
perc = 99.9

# --- Prepare the Hovmöller grid: shape (n_months, n_years) ---
M = len(mos)
Y = len(yrs)
H = np.full((M, Y), np.nan)  # will hold the 99.5th percentile latitude per (month, year)
lat_max_ipc = []

for iy, yr in enumerate(yrs):
    origin_file = f'{results_folder}/Lon_Lat_Origin_{yr}_year.nc'
    ds = xr.open_dataset(origin_file, decode_times=True)

    for im, mo in enumerate(mos):
        # Select month
        ds_mo = ds.where(ds['month'] == mo, drop=True)

        # Pull arrays; use .values and ravel to ensure flat arrays for boolean indexing
        lat_ini     = np.asarray(ds_mo['lat_00'].values).ravel()
        origin_age  = np.asarray(ds_mo[f'origin_{age:02d}'].values).ravel()

        # Filter by origin and compute the 99.5th percentile if we have data
        lat_orig = lat_ini[origin_age == orig]
        if lat_orig.size > 0:
            H[im, iy] = np.percentile(lat_orig, perc)
        else:
            H[im, iy] = np.nan  # keep NaN for missing data
        lat_max_ipc.append(np.percentile(lat_orig, perc))   
        

# calculate seasonal cycle
H_monthly_clim = np.nanmean(H, axis=1)   # shape = (12,)
H_monthly_std = np.nanstd(H, axis=1)   # shape = (12,)
H_clim_2d = np.tile(H_monthly_clim[:, None], (1, H.shape[1]))
H_anom = H - H_clim_2d

# calculate yearly anomalies
H_yearly_anom = np.nanmean(H_anom, axis=0) 
H_yearly_std = np.nanstd(H_anom, axis=0) 

x = np.arange(Y)
y = np.arange(M)


# arrange everything to go from Jul year = i to Jun year i+1
H_yearly_anom = np.array([
    np.nanmean(np.r_[H_anom[6:, i], H_anom[:6, i+1]])
    for i in range(len(yrs)-1)
])

H_yearly_std = np.array([
    np.nanstd(np.r_[H_anom[6:, i], H_anom[:6, i+1]])
    for i in range(len(yrs)-1)
])



x=x[0:-1]

month_labels = list(calendar.month_abbr[1:13])
month_labels = month_labels[6:] + month_labels[:6]


H_monthly_clim = np.r_[H_monthly_clim[6:], H_monthly_clim[:6]]
H_monthly_std  = np.r_[H_monthly_std[6:], H_monthly_std[:6]]





# --------------------------
# --- Plot the Hovmöller ---
# --------------------------


fig = plt.figure(figsize=(6.8,3.4))

# GridSpec: 2 rows, 2 columns
# Row 0: only one panel across both columns
# Row 1: narrow left (seasonal cycle) + wide right (Hovmöller)
gs = gridspec.GridSpec(
    2, 2,
    height_ratios=[1.2, 4],      # top row is smaller
    width_ratios=[0.6, 4],    # left column is very narrow
    hspace=0.1,
    wspace=0.05
)

# -----------------------------------------------
# (A) Top panel — Yearly anomaly time series
# -----------------------------------------------
ax_top = fig.add_subplot(gs[0, 1])    

ax_top.plot(x, H_yearly_anom, marker='o', color='black', markersize=2)
ax_top.fill_between(
    x,
    H_yearly_anom - H_yearly_std,
    H_yearly_anom + H_yearly_std,
    color='gray', edgecolor='none',
    alpha=0.3,
    label='±1 std'
)
ax_top.axhline(0, color='gray', linewidth=0.8)

ax_top.set_ylabel("Latitude\nanom. [°N]")
#ax_top.set_title(f"Yearly-averaged anomalies of max latitude of {area_labels[orig-1]} water ({age} days)")

# Share x-axis with the Hovmöller → ticks only on bottom panel
ax_top.set_xticks(x)
ax_top.set_xticklabels([])
ax_top.text(0.5,-0.6,'(a)')

# --------------------
# (B) LEFT panel: Seasonal cycle (narrow)
# --------------------
ax_left = fig.add_subplot(gs[1,0])

ax_left.plot(H_monthly_clim, y, marker='o', color='black',markersize=2)
ax_left.fill_betweenx(
    y,
    H_monthly_clim - H_monthly_std,
    H_monthly_clim + H_monthly_std,
    color='gray', edgecolor='none',
    alpha=0.3,
    label='±1 std'
)

ax_left.set_xticks([46,47,48])
ax_left.set_ylim(M-0.5, -0.5)  # match Hovmöller orientation

# Month ticks on left panel
ax_left.set_yticks(y)
ax_left.set_yticklabels([month_labels[m-1][0] for m in mos])

ax_left.set_xlabel('Latitude [°N]')
#ax_left.set_title('Seasonal cycle')
ax_left.text(47.5,1,'(b)')

# Add a box around this axis
for spine in ax_left.spines.values():
    spine.set_visible(True)
    spine.set_linewidth(1.1)



# --------------------
# (C) RIGHT panel: Hovmöller anomaly
# --------------------
ax_hov = fig.add_subplot(gs[1,1])

# data_anom = np.ma.masked_invalid(H_anom)
# cmap = plt.get_cmap('RdBu_r').copy()
# cmap.set_bad(color='lightgray')

# mesh = ax_hov.pcolormesh(x, y, data_anom, cmap=cmap, shading='nearest')

# --- build H_anom matrix to go from Jul year to Jun year +1
n_years = len(yrs)
H_anom_jj = np.full((12, n_years - 1), np.nan)
for iy in range(n_years - 1):
    H_anom_jj[:, iy] = np.r_[
        H_anom[6:, iy],      # Jul-Dec current year
        H_anom[:6, iy + 1]   # Jan-Jun next year
    ]


data_anom = np.ma.masked_invalid(H_anom_jj)
mesh = ax_hov.pcolormesh(x, y, data_anom, cmap=cmap, shading='nearest')

ax_hov.set_yticks(y)
ax_hov.set_yticklabels(month_labels)


# --- Compute trend + significance ---
lat_max_ipc = np.array(lat_max_ipc)   # shape = (Y*M,)

# Build a month index array: 0..11 repeating
month_idx = np.tile(np.arange(12), len(yrs))

# Compute anomalies
lat_max_anom = lat_max_ipc - H_monthly_clim[month_idx]

t = np.arange(len(lat_max_anom))
slope, intercept, r_value, p_value, stderr = linregress(t, lat_max_anom)

# Add the trend text to the plot
plt.text(
    0.05, 0.2,
    f"trend = {slope:.4f} [°N] month$^{{-1}}$\npval = {p_value:.3g}",
    transform=ax_hov.transAxes,
    verticalalignment="top",
)

ax_hov.set_xticks(x)
#ax_hov.set_xticklabels([str(yy) for yy in yrs[:-1]], rotation=90)

ax_hov.set_xticklabels([f'{y%100:02d}/{(y+1)%100:02d}' for y in yrs[:-1]],rotation=90)





# Month labels on left panel only → so hide these
ax_hov.set_yticks(y)
ax_hov.set_yticklabels([])

ax_hov.set_xlabel('Seasonal Year (Jul–Jun)')
ax_hov.invert_yaxis()

ax_hov.text(0.5,1,'(c)')

# Optional: set color scale limits if you want consistent scaling
vmin, vmax = -1.2, 1.2
mesh.set_clim(vmin=vmin, vmax=vmax)
cbar = fig.colorbar(mesh, ax=ax_hov, pad=0.02)
cbar.set_label('Latitude anomaly [°N]')



# --- MATCH ax_top WIDTH TO ax_hov WIDTH ---
# Get pixel bounds of the Hovmöller axis
hov_pos = ax_hov.get_position()
top_pos = ax_top.get_position()
ax_top.set_position([
    hov_pos.x0,
    top_pos.y0,
    hov_pos.width,
    top_pos.height
])


ax_top.set_xlim(ax_hov.get_xlim())
ax_top.margins(x=0)


plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8
})

plt.show()
fig.tight_layout()


fig.savefig(f'{plot_folder}/Figure_10_Northward_extent.png',bbox_inches='tight')

