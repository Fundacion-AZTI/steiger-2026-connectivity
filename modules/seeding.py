#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 10:00:46 2025

Function to create seeding for connectivity study

@author: nsteiger
"""
import numpy as np
from scipy.interpolate import RegularGridInterpolator

def create_seeding_grid(lon_min, lon_max, lat_min, lat_max, res):
    
    lo = np.arange(lon_min, lon_max + res, res)
    la = np.arange(lat_min, lat_max + res, res)
    
    return np.meshgrid(lo,la)


def apply_land_mask(lat_grid,lon_grid,bathy_data):
    # Apply landmask from bathymetry file to mask points on land

    mask = np.zeros(bathy_data['depth'].shape)
    mask[bathy_data['depth']>0]=1

    interp_mask = RegularGridInterpolator((bathy_data['lat'], bathy_data['lon']), mask, bounds_error=False, fill_value=None)
    mask_int = interp_mask((lat_grid.flatten(), lon_grid.flatten()))

    valid_indices = mask_int == 0  & (~np.isnan(mask_int)) # ocean points

    return lon_grid.flatten()[valid_indices], lat_grid.flatten()[valid_indices]


def save_seeding_coords(lon, lat, res, seeding_file):
    # save seeding coordinates
    coords = np.vstack((lon,lat))
    coords_T = coords.T
    np.savetxt(seeding_file,coords_T,fmt='%.6f',delimiter='')