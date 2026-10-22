This repository contains scripts that accompany paper Steiger et al. 2026.

It is organized in three folders for running opendrift simulations, then process data to calculate matrices and then plot the figures. 


N. Steiger 20/10/2026

------------------------
----- python -----------
------------------------

All scripts are written in python and executed with version 3.13.5. 
The virtual environment used for running the opendrift simulations and the analysis of the output is provided as environment_opendrift.yml


------------------------
---- content -----------
------------------------


........................
1. SIMULATIONS_OPENDRIFT 

contains scripts to run open drift simulations with regularly seeded particles in the Bay of Biscay as backward simulations over 120 days seeding throughout each month and year from 1993 to 2025: 

- driver.py: Main script to be run. Overarching script that indicates year and month to loop over and run drift simulation on. It calls run_connectivity_simulation_subprocess.py to execute the simulations as subprocess for each year and month, which allows the workspace to be cleaned after each simulation to avoid memory overcharge. 

- run_connectivity_simulation_subprocess.py: reads the year and month given by driver.py and uses functions defined in scripts within general modules. 
Acesses Folder for simulation that needs to be specified



........................
2. FOLDER FOR SIMULATION SPECIFICATION AND OUTPUT

- config.py: defines parameters specific to the setup used for this simulation (diffusion coefficient, time step etc)

- figures: directory for figures and animations created by OpenDrift

- output: directory to save netcdf output files from OpenDrift



......................
3. MODULES

contains scripts with functions related to seeding, simulation and visualization. 




.........................
4. ANALYSIS_PROCESSING


contains scripts to post-process data and calculate metrices used for plotting


- reduce_outfile.py: remove data that were saved but not needed to reduce file size; also add variable area, which is from 1-9 the name of the area where the trajectory is currently located

- save_lon_lat_origin.py: saves for 7,30 and 90 days and for each trajectory the lon, lat, seed, time, origin in a 
Input: Connectivity_ibi_backward_0.08deg_-900s_{yr}_{mo:02d}_{config.sim_name}.nc'
Output: Lon_Lat_origin_{yr}_year.nc

- analyse_mixing.py: 
Calculates Origin diversity index based on number of origins at each lon lat grid point on a regular grid
Input: netcdf from reduced data. 
Output: mixing_{age}_{yr}.nc


- analyse_connectivity_matrix.py: 
Calculates connectivity matrix monthly, yearly means and climatology, as well as trend, and detrended. 
Input: netcdf from origin - Lon_Lat_origin_{yr}_year.nc. 
Output: Connectivity_matrix_{age}days_coast_previous_seeding5days.pkl and csv. Also other files of clim, mean, trend,pval etc


................................
5. PLOTTING

contains scripts to plot all the figures contained in the paper. 


.................................
6. WEBAPP 

contains scripts to plot figures in the webapp that accompanies the paper. 





