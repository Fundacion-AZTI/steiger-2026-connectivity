#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 09:32:11 2025

Main script for OpenDrift simulations within the Bay of Biscay with seeding over a regular grid

This scripts calls the following functions:
- load_config: for general simulation configurations
- read_bathymetry: read bathymetry data
- create_seeding_grid: create grid for seeding 
- setup_model: setup reader and config
- seed_and_run: seed elements and run model
- general_output: create plot and animation


@author: nsteiger
"""

import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# Import shared modules
from modules.read_data import read_bathymetry
from modules.seeding import create_seeding_grid, apply_land_mask, save_seeding_coords
from modules.simulation import setup_model, seed_and_run
from modules.visualization import generate_outputs
from modules.load_config import load_config
from modules.file_names import create_file_names

import argparse



# Read year and months from driver.py script to loop over years and months
parser = argparse.ArgumentParser()
parser.add_argument("--year", type=int, required=True)
parser.add_argument("--month", type=int, required=True)
args = parser.parse_args()

yr = args.year
mo = args.month

# Ensure mo and yr are always lists
#mos = months if isinstance(months, (list, tuple)) else [months]
#yrs = years if isinstance(years, (list, tuple)) else [years]


print(f"Running simulation for {yr}-{mo:02d}")


# Choose which simulation to run -- CHANGE THIS PATH TO YOUR SIMULATION PATH WHETE TO OUTPUT RESULTS
simulation_folder = '/data2/nadine/github/steiger-2026-connectivity/2026_01_08_seeding5days_1993-2024'  # Change this to the correct folder




# Load the config for the selected simulation
config = load_config(simulation_folder)

print('Configuration loaded')



if hasattr(config, 'out_file'):
	out_file = config.out_file
	plot_file = config.plot_file
	animation_file = config.animation_file
	seeding_file = config.seeding_file            
else: # if no filenames indicated in config, use function 'create_file_name'
	if hasattr(config, 'sim_name'): # if sim_name is given in config file, use it
		out_file, plot_file, animation_file, seeding_file = create_file_names(config.res, config.dt, yr, mo, simulation_folder,config.sim_name)
	else:
            out_file, plot_file, animation_file, seeding_file = create_file_names(config.res, config.dt, yr, mo, simulation_folder)


print(f'Output will be saved in {out_file}')

# Read data
#current_data = read_current_data(config.current_file)
bathy_data = read_bathymetry(config.bathy_file)
        
print('Done reading current and bathymetry data') 

# Create seeding grid
lon_grid, lat_grid = create_seeding_grid(config.lon_min, config.lon_max, config.lat_min, config.lat_max, config.res)
lon, lat = apply_land_mask(lat_grid, lon_grid, bathy_data)
save_seeding_coords(lon, lat, config.res, seeding_file)
        
print('Seeding is set up')

# Run simulation
o = setup_model(config.current_file, config.diff, config.coastl_action, yr, mo)
        
if hasattr(config, 'exp_variables'):
	o = seed_and_run(o, lon, lat, yr, mo, config.dt, config.time_step_seeding, config.duration, out_file, config.exp_variables)
else:  # if no export variables indicated, export all variables
	o = seed_and_run(o, lon, lat, yr, mo, config.dt, config.time_step_seeding, config.duration, out_file)
print('Model simulations are done')

# Generate plots and animation
generate_outputs(o, plot_file, animation_file)
        
print(f'Simulation for {yr}-{mo:02d} successfully completed.')

