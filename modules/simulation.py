#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 10:59:06 2025

Start simulations

@author: nsteiger
"""
from opendrift.readers import reader_netCDF_CF_generic
from opendrift.models.oceandrift import OceanDrift
from datetime import timedelta, datetime

def setup_model(current_file, diff, coastl_action,yr=None,mo=None):
    
    # Set parameters for opendrift model
    o=OceanDrift(loglevel=50)  
    if yr==None:  # read whole velocity netcdf file that contains all years
        reader_curr = reader_netCDF_CF_generic.Reader(current_file)
    else:  # read only velocity netcdf file needed for the simulation
        if mo<4:
            reader_curr = reader_netCDF_CF_generic.Reader(f'/data2/BIOCEAN5D/Data/Currents/ibi_hourly_by_year/ONDJFM_{yr-1}_{yr}.nc')
        else:
            reader_curr = reader_netCDF_CF_generic.Reader(f'{current_file}_{yr}.nc')     
    print(reader_curr)                                         
    #reader_wind = reader_netCDF_CF_generic.Reader(wind_file)
    o.add_reader([reader_curr])
    o.set_config('drift:horizontal_diffusivity', diff)     # Difference from first run
    o.set_config('general:coastline_action',coastl_action)     # To keep elements at coast until moved offshore at a later time
    o.list_configspec()
    
    return o
    
    
def seed_and_run(o, lon, lat, yr, mo, dt, time_step_seeding, duration, out_file, exp_variables='all'):
    # Determine seeding and run model
    
    #dt and time_step_seeding must be in seconds

    t1=datetime(yr, mo, 1, 0, 0, 0)
    
    if time_step_seeding==0:
        print(t1)
        o.seed_elements(lon,lat,time=t1) #one particle per (lon,lat) pair
    else:
        for i in time_step_seeding:
            seed_time = t1 + timedelta(days=i)
            print(seed_time)
            o.seed_elements(lon,lat,time=seed_time)
    
    if exp_variables=='all':
        o.run(duration=timedelta(days=duration), time_step=dt, time_step_output=86400, outfile=out_file) 
    else:
        o.run(
            duration=timedelta(days=duration), 
            time_step=dt, 
            time_step_output=86400, 
            outfile=out_file, 
            export_variables=exp_variables
        )
  #  print(o.get_status())
    
    return o
