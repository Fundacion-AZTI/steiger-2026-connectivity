#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 25 11:21:38 2025

Connectivity matrix between defined areas for OpenDrift simulations 
- after 9 days
- after 30 days
- after 90 days

1. Load paths and modules
2. Loop through simulations and calculate connectivity matrix for all months and years -> save as csv and pickle
3. Calculate and save climatologies (monthly means) -> save as *monthly_mean* csv and pickle
4. Calculate and save all-time mean -> save as *all_mean* csv and pickle
5. Only save areas interested in (i.e. for matrixes only at shelf)
6. Calculate and save trend and pvalue of connectivity matrix -> save as *trend*, *pval* as vsc and pickle

Connectivity matrixes can later be vizualized with plot_connectivity_matrix.py, vizualise_connectivity_matrix.py and plot_connectivity_trend.py

@author: nsteiger
"""

# In[1]
# General preparation of the data 
import pandas as pd
import numpy as np
from scipy.stats import linregress
import netCDF4 as nc


# --- paths ---- CHANGE THESE
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
out_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/connectivity/'
in_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/origin/'


# -- general settings-----
legend_colors =['red','cyan','green','orange','blue','purple','yellow','gray']
legend_labels = ['south', 'west', 'north', 'fr_shelf', 'es_shelf', 'fr_slope', 'es_slope', 'deep']
bathy_levels = [-1000,-200,0]


sim_name = 'coast_previous_seeding5days' 



# In[2]
# define functiones needed

# calculate connectivity matrix using age
def calc_connectivity_matrix_new(origin_00,origin_age,area_labels):
    # select lon at lat of all trajectories of given age
        
    nb_areas = len(area_labels)
    
    M=np.full((nb_areas,nb_areas),np.nan)

    for i in range(nb_areas):
        for j in range(nb_areas):
                denominator = np.nansum(origin_00 == i+1)
                if denominator != 0:
                    M[i,j] = np.nansum((origin_00 == i+1) & (origin_age == j+1)) / denominator * 100
                else:
                    M[i,j] = np.nan  
     
  #  M = np.round(M)
    if nb_areas>3: 
        M = M[3:nb_areas, :]  # your slicing
        row_headers = area_labels[3:]
    else:
        row_headers = area_labels
    column_headers = area_labels  # origin of particles
    df = pd.DataFrame(M, columns=column_headers, index=row_headers)
    return df




# In[3]
# Calculate connectivity matrix for all simulations

mos = range(1,13)
yrs = range(1994,2025)
area_labels = legend_labels

ages = [7,30,90]


for age in ages:
    M_all = []
    for i, yr in enumerate(yrs):
        for j, mo in enumerate(mos):
            out_file = f'{in_folder}Lon_Lat_Origin_{yr}_year.nc'
            print(f"Processing: {out_file} for month {mo:02d}")
            drift_data = nc.Dataset(out_file, model='r')
            origin_00 = drift_data.variables['origin_00'][j,:] # read seeding position for month j
            origin_age = drift_data.variables[f'origin_{age:02d}'][j,:] # read origion position at age=age for monthj
            df = calc_connectivity_matrix_new(origin_00,origin_age,area_labels)
            print(df)
            df['year'] = yr
            df['month'] = mo
            df = df.reset_index().rename(columns={'index': 'seeding_area'})
            #df.to_csv(f'results/Connectivity_matrix_{age}days_{yrs}_{mos:02d}_{config.sim_name}.csv', float_format='%.0f')
            M_all.append(df)
            
    
    # Combine into one big DataFrame
    M_final = pd.concat(M_all)
    M_final = M_final.set_index(['year', 'month','seeding_area'])
    
    # Save to disk
    M_final.to_pickle(f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl')  # preserves arrays if needed
    M_final.to_csv(f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.csv', index=True, float_format='%.0f')  # for easy sharing

    print(f"Connectivity matrix saved as Connectivity_matrix_{age}days_{sim_name}.csv")

            
            
# In[3]
# Calculate climatologies

ages = [7,30,90]

for age in ages:
    M_file = f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl'
    M = pd.read_pickle(M_file)
    # Group by month and seeding area and calculate mean across all years
    M_monthly_mean = M.groupby(['month', 'seeding_area']).mean(numeric_only=True)
    M_monthly_mean.to_pickle(f'{out_folder}/Connectivity_matrix_{age}days_monthly_mean_{sim_name}.pkl')  # preserves arrays if needed
    M_monthly_mean.to_csv(f'{out_folder}/Connectivity_matrix_{age}days_monthly_mean_{sim_name}.csv', index=True, float_format='%.0f')  # for easy sharing


# In[4]
# Calculate mean over months and years

ages = [7,30,90]
for age in ages:
    M_file = f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl'
    M = pd.read_pickle(M_file)
    # Group by seeding area and calculate mean
    M_mean = M.groupby(['seeding_area']).mean(numeric_only=True)
    M_mean.to_pickle(f'{out_folder}/Connectivity_matrix_{age}days_all_mean_{sim_name}.pkl')  # preserves arrays if needed
    M_mean.to_csv(f'{out_folder}/Connectivity_matrix_{age}days_all_mean_{sim_name}.csv', index=True, float_format='%.0f')  # for easy sharing



# In[5]
# Only save areas I am interested in

areas=['fr_shelf','es_shelf']
ages = [7,30,90]
for age in ages:
    M_file = f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl'
    M = pd.read_pickle(M_file)
    # Group by seeding area and calculate mean
    M_mean = M.groupby(['month','seeding_area']).mean(numeric_only=True)
    
    # extract only areas that I want to save in csv file
    M_subset = M_mean.loc[M_mean.index.get_level_values('seeding_area').isin(areas), areas]

    M_subset.to_csv(f'{out_folder}/Connectivity_matrix_fr_es_shelf_{age}days_monthly_mean_{sim_name}.csv', index=True, float_format='%.0f')  # for easy sharing



# In[6]
# Calculate trend of connectivity over all time steps

ages = [7,30,90]
for age in ages:
    M_file = f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl'
    M = pd.read_pickle(M_file)
    # Group by seeding area and calculate trend
    

    # Step 1: Reset index and create a numeric time axis
    M_reset = M.reset_index()
    M_reset['time_num'] = (M_reset['year'] - M_reset['year'].min()) * 12 + (M_reset['month'] - 1)
    
    # Step 2: Identify numeric columns
    numeric_cols = M_reset.select_dtypes(include=[np.number]).columns.drop(['year', 'month', 'time_num'])
    
    # Step 3: Function to compute slope, intercept, R² for each numeric column
    def compute_trend(group):
        results = {}
        for col in numeric_cols:
            x = group['time_num'].values
            y = group[col].values
            if len(x) < 2 or np.all(y == y[0]):  # Not enough variation
                results[f'{col}_trend'] = np.nan
              #  results[f'{col}_intercept'] = np.nan
              #  results[f'{col}_r2'] = np.nan
                results[f'{col}_pval'] = np.nan
            else:
                res = linregress(x, y)
                results[f'{col}_trend'] = res.slope
               # results[f'{col}_intercept'] = res.intercept
               # results[f'{col}_r2'] = res.rvalue**2
                results[f'{col}_pval'] = res.pvalue
        return pd.Series(results)

    
    # Step 4: Apply per seeding_area
    M_trend = M_reset.groupby('seeding_area').apply(compute_trend)
    
    # Step 5: Separate matrix to have slope and r2 in separate matrixes
    slope_cols = [c for c in M_trend.columns if c.endswith('_trend')]
    pval_cols = [c for c in M_trend.columns if c.endswith('_pval')]
    
    M_slope = M_trend[slope_cols].rename(columns=lambda c: c.replace('_trend',''))
    M_pval = M_trend[pval_cols].rename(columns=lambda c: c.replace('_pval',''))

    
    print(M_slope)
    print(M_pval)

    M_slope.to_pickle(f'{out_folder}/trend/Connectivity_matrix_{age}days_trend_{sim_name}.pkl')  # preserves arrays if needed
    M_pval.to_pickle(f'{out_folder}/trend/Connectivity_matrix_{age}days_pval_{sim_name}.pkl')  # preserves arrays if needed
    M_slope.to_csv(f'{out_folder}/trend/Connectivity_matrix_{age}days_trend_{sim_name}.csv', index=True, float_format='%.4f')  # for easy sharing
    M_pval.to_csv(f'{out_folder}/trend/Connectivity_matrix_{age}days_pval_{sim_name}.csv', index=True, float_format='%.4f')  # for easy sharing
    
    
    
    
# In[6]
# Calculate trend of DESEASONED connectivity over all time steps

ages = [7,30,90]
for age in ages:

    M_file = f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl'
    M = pd.read_pickle(M_file)
    
    # Step 1: Reset index and create a numeric time axis
    M_reset = M.reset_index()
    M_reset['time_num'] = (M_reset['year'] - M_reset['year'].min()) * 12 + (M_reset['month'] - 1)
    
    # Step 2: Identify numeric connectivity columns
    numeric_cols = M_reset.select_dtypes(include=[np.number]).columns.drop(['year', 'month', 'time_num'])
    
    # Step 3: Compute monthly climatology
    M_monthly_mean = M_reset.groupby(['month', 'seeding_area']).mean(numeric_only=True)
    
    # Step 4: Align climatology to full dataset
    M_idx = M_reset.set_index(['month','seeding_area'])
    monthly_mean_aligned = M_monthly_mean.reindex(M_idx.index)
    
    # Step 5: Subtract monthly mean only from connectivity columns
    M_anom_numeric = M_idx[numeric_cols] - monthly_mean_aligned[numeric_cols]
    
    # Step 6: Reinsert anomaly into dataframe, keep other columns unchanged
    M_anom = M_idx.copy()
    M_anom[numeric_cols] = M_anom_numeric
    
    # Step 7: Restore index to columns
    M_anom = M_anom.reset_index()


    # Step 3: Function to compute slope, intercept, R² for each numeric column
    def compute_trend(group):
        results = {}
        for col in numeric_cols:
            x = group['time_num'].values
            y = group[col].values
            if len(x) < 2 or np.all(y == y[0]):  # Not enough variation
                results[f'{col}_trend'] = np.nan
              #  results[f'{col}_intercept'] = np.nan
              #  results[f'{col}_r2'] = np.nan
                results[f'{col}_pval'] = np.nan
            else:
                res = linregress(x, y)
                results[f'{col}_trend'] = res.slope
               # results[f'{col}_intercept'] = res.intercept
               # results[f'{col}_r2'] = res.rvalue**2
                results[f'{col}_pval'] = res.pvalue
        return pd.Series(results)

    
    # Step 4: Apply per seeding_area
    M_trend = M_anom.groupby('seeding_area').apply(compute_trend)
    
    # Step 5: Separate matrix to have slope and r2 in separate matrixes
    slope_cols = [c for c in M_trend.columns if c.endswith('_trend')]
    pval_cols = [c for c in M_trend.columns if c.endswith('_pval')]
    
    M_slope = M_trend[slope_cols].rename(columns=lambda c: c.replace('_trend',''))
    M_pval = M_trend[pval_cols].rename(columns=lambda c: c.replace('_pval',''))

    
    print(M_slope)
    print(M_pval)

    M_slope.to_pickle(f'{out_folder}/trend/Connectivity_matrix_{age}days_trend_deseasoned_{sim_name}.pkl')  # preserves arrays if needed
    M_pval.to_pickle(f'{out_folder}/trend/Connectivity_matrix_{age}days_pval_deseasoned_{sim_name}.pkl')  # preserves arrays if needed
    M_slope.to_csv(f'{out_folder}/trend/Connectivity_matrix_{age}days_trend_deseasoned_{sim_name}.csv', index=True, float_format='%.4f')  # for easy sharing
    M_pval.to_csv(f'{out_folder}/trend/Connectivity_matrix_{age}days_pval_deseasoned_{sim_name}.csv', index=True, float_format='%.4f')  # for easy sharing
    

# In[7]
# Calculate trend of connectivity for each month separately - note that less data is included, so significance goes down!

ages = [7, 30, 90]

for age in ages:
    M_file = f'{out_folder}/Connectivity_matrix_{age}days_{sim_name}.pkl'
    M = pd.read_pickle(M_file)

    # Prepare accumulators
    all_slope = []
    all_pval = []

    # List months to process
    months = range(1, 13)

    for month in months:
        M_month = M[M.index.get_level_values('month') == month]
        M_reset = M_month.reset_index()

        # numeric time axis
        M_reset['time_num'] = (M_reset['year'] - M_reset['year'].min()) * 12 + (M_reset['month'] - 1)

        # numeric connectivity columns
        numeric_cols = (
            M_reset.select_dtypes(include=[np.number])
            .columns.drop(['year', 'month', 'time_num'])
        )

        # compute trend per seeding area
        def compute_trend(group):
            results = {}
            for col in numeric_cols:
                x = group['time_num'].values
                y = group[col].values

                if len(x) < 2 or np.all(y == y[0]):
                    results[f'{col}_trend'] = np.nan
                    results[f'{col}_pval'] = np.nan
                else:
                    res = linregress(x, y)
                    results[f'{col}_trend'] = res.slope
                    results[f'{col}_pval'] = res.pvalue
            return pd.Series(results)

        # compute slope/pval tables
        M_trend = M_reset.groupby('seeding_area').apply(compute_trend)

        # extract slope / pval matrices
        slope_cols = [c for c in M_trend.columns if c.endswith('_trend')]
        pval_cols  = [c for c in M_trend.columns if c.endswith('_pval')]

        M_slope = M_trend[slope_cols].rename(columns=lambda c: c.replace('_trend',''))
        M_pval  = M_trend[pval_cols].rename(columns=lambda c: c.replace('_pval',''))

        # add month index
        M_slope['month'] = month
        M_pval['month']  = month

        # store
        all_slope.append(M_slope.set_index('month', append=True))
        all_pval.append(M_pval.set_index('month', append=True))

    # concatenate all months
    slope_final = pd.concat(all_slope).reorder_levels(['month', 'seeding_area']).sort_index()
    pval_final  = pd.concat(all_pval).reorder_levels(['month', 'seeding_area']).sort_index()

    print(slope_final)
    print(pval_final)

    # save
    slope_final.to_pickle(f'{out_folder}/Connectivity_matrix_{age}days_trend_allMonths_{sim_name}.pkl')
    pval_final.to_pickle(f'{out_folder}/Connectivity_matrix_{age}days_pval_allMonths_{sim_name}.pkl')

    slope_final.to_csv(f'{out_folder}/Connectivity_matrix_{age}days_trend_allMonths_{sim_name}.csv',float_format='%.4f')
    pval_final.to_csv(f'{out_folder}/Connectivity_matrix_{age}days_pval_allMonths_{sim_name}.csv',float_format='%.4f')



