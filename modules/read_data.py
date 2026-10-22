#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 09:41:02 2025

Read current and bathymetry data used for OpenDrift simulations

@author: nsteiger
"""


import netCDF4 as nc

def read_current_data(current_file):
    nc_ibi = nc.Dataset(current_file, model='r')
    timestamp = nc_ibi.variables['time']
    time = nc.num2date(timestamp[:], units=timestamp.units, calendar=timestamp.calendar)
    return {
        'lon': nc_ibi.variables['longitude'][:],
        'lat': nc_ibi.variables['latitude'][:],
        'uo': nc_ibi.variables['uo'],
        'time': time
    }

def read_bathymetry(bathy_file):
    bathy_data = nc.Dataset(bathy_file, model='r')
    return {
        'lon': bathy_data.variables['lon'][:],
        'lat': bathy_data.variables['lat'][:],
        'depth': bathy_data.variables['elevation'][:]
    }

from datetime import datetime
def read_driftdata(drift_file):
    drift_data = nc.Dataset(drift_file, model='r')
    timestamp = drift_data.variables['time'][:]
    formatted_times = [datetime.fromtimestamp(ts) for ts in timestamp]
    if 'status' in drift_data.variables:
        return {
            'lon': drift_data.variables['lon'][:],
            'lat': drift_data.variables['lat'][:],
            'age_seconds': drift_data.variables['age_seconds'][:],
            'origin_marker': drift_data.variables['origin_marker'][:],
            'status': drift_data.variables['status'][:],
            'time': formatted_times
        }
    else:
        return {
            'lon': drift_data.variables['lon'][:],
            'lat': drift_data.variables['lat'][:],
            'age_seconds': drift_data.variables['age_seconds'][:],
            'origin_marker': drift_data.variables['origin_marker'][:],
            'time': formatted_times
        }        
