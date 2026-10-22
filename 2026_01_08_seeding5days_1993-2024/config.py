#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 11:40:16 2025

@author: nsteiger
"""

from datetime import datetime

diff=0
coastl_action = 'previous'


lon_min = -11
lon_max = -1
lat_min = 41
lat_max = 48.5


# mo=[1,2,3,4,5,6,7,8,9,10,11,12]	#start month
# yr=[1996,1997,1998,1999]  #start year: ibi surface currents downloaded from 01.01.1991 - 31.12.2024


res=0.08  #grid resolution for the seeding - choose between 1, 0.5, 0.2, 0.08
dt=-900  #in seconds; negative value for backward trajectories (900 should be good - 1/4 of time resolution of forcing data = 1h)

duration = 120  #days of simulation runs -> last seeding (at end of month) will have duration of duration-30
time_step_seeding = range(0,31,5) #time step in days for the seeding; if 0, seeding will only happen on the first day of simulation

today_str = datetime.today().strftime('%Y%m%d')

# path for current forcing file and bathymetry file
#current_file = '/data2/BIOCEAN5D/Data/Currents/cmems_mod_ibi_phy_my_0.083deg-2D_PT1H-m_vo-uo_11.00W-1.00W_41.00N-48.50N_2013-11-01-2023-11-01.nc'
#current_file = '/data2/BIOCEAN5D/Data/Currents/cmems_mod_ibi_phy_my_0.083deg-2D_PT1H-m_vo-uo_13.00W-1.00W_39.00N-50.50N_2013-11-01-2023-11-01.nc'

current_file = '/data2/BIOCEAN5D/Data/Currents/ibi_hourly_by_year/cmems_mod_ibi_phy-cur_my_0.027deg_PT1H-m_13.00W-1.00W_39.00N-50.50N'

bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
#bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_17_Sep_2025/gebco_2025_n48.5_s41.0_w-11.0_e-1.0.nc'
#wind_file = ''

sim_name = 'coast_previous_seeding5days'  # ending that will be added to filename
exp_variables = ['lon',
                 'lat',
                 'age_seconds',
                 'origin_marker',
                 'status',
                 'time',
                 'trajectory',
                 'moving'
                 ]


area_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
area_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']

