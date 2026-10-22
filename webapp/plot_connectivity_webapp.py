#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Sep 22 13:04:09 2026

@author: nsteiger
"""


# In[1]


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.axes_grid1 import make_axes_locatable


# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/webapp/figures/connectivity/'
connectivity_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/connectivity/'


# -- general settings-----
areas = ['fr_shelf', 'fr_slope', 'es_shelf', 'es_slope','deep']
areas_all = ['south','west','north','fr_shelf', 'fr_slope', 'es_shelf', 'es_slope','deep']






def plot_connectivity_matrix(heatmap_data,age):

   # Plot with Seaborn
   fig, ax = plt.subplots(figsize=(5,3.5))

   divider = make_axes_locatable(ax)
   cax = divider.append_axes("right", size="4%", pad=0.1)  # ← decrease pad

   sns.heatmap(heatmap_data, cmap="viridis", vmin=0, vmax=100, annot=True, fmt=".0f", ax=ax, cbar_ax=cax, cbar_kws={'label':'Connectivity [%]'})
   #ax.set_title(f"Connectivity matrix for {age:02d} days {mo:02d}/{yr}")
   ax.set_xlabel(f"Origin subarea ({age:02d} days)")
   ax.set_ylabel("Seeding subarea")
   
   ax.tick_params(axis='y', labelrotation=0)
   ax.tick_params(axis='x', labelrotation=60)
   
   
   # Vertical line between column 3 and 4
   ax.axvline(x=3, color='gray', linewidth=2)

   # --- Highlight diagonal ---
   for i in range(heatmap_data.shape[0]):
       ax.add_patch(plt.Rectangle((i+3, i), 1, 1, fill=False,
                                  edgecolor='gray', linewidth=2))

   
   # Draw a box around the heatmap
   for spine in ax.spines.values():
       spine.set_visible(True)
       spine.set_linewidth(0.5)   # thickness of the box
       spine.set_color("gray") # color of the box
   

   plt.rcParams.update({
       "font.size": 8,
       "axes.labelsize": 8,
       "xtick.labelsize": 8,
       "ytick.labelsize": 8
   })
   
   return fig, ax




# In[2]  CONNECTIVITY MATRIX of each month
# Vizualise connectivity matrix 
ages=[7,30,90]
mos = np.arange(1,13)
yrs = np.arange(1994,2025)

for i, age in enumerate(ages):
    df_all = pd.read_csv(f"{connectivity_folder}/Connectivity_matrix_{age}days_coast_previous_seeding5days.csv")
    
    for k, yr in enumerate(yrs):
        df_year = df_all[df_all['year']==yr]   #only select one year
        
        for j, mo in enumerate(mos):
            df = df_year[df_year['month']==mo]   #only select one month
            
            df['row_id'] = df['seeding_area']
            
            # Sort rows globally by seeding area: first all Bizkaia, then Gipuzkoa, then France
            order = []
            for area in areas:
                order.append(f"{area}")
            
            # Prepare heatmap data with correct global order
            heatmap_data = df.set_index('row_id')[areas_all].loc[order]
            
            
            fig, ax = plot_connectivity_matrix(heatmap_data,age)
            ax.set_title(f"Connectivity matrix for {mo:02d}/{yr}")
        
            # Save as PNG 
            plt.tight_layout()
            plt.savefig(f"{plot_folder}/Connectivity_{age:02d}_{yr}_{mo:02d}.png", dpi=300, bbox_inches='tight')        







# In[3]  CONNECTIVITY MATRIX of MONTHLY MEAN
# Vizualise connectivity matrix 
ages=[7,30,90]
mos = np.arange(1,13)
months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']

for i, age in enumerate(ages):
    df_all = pd.read_csv(f"{connectivity_folder}/Connectivity_matrix_{age}days_monthly_mean_coast_previous_seeding5days.csv")
    
    
    for j, mo in enumerate(mos):
        df = df_all[df_all['month']==mo]   #only select one month
        
        df['row_id'] = df['seeding_area']
        
        # Sort rows globally by seeding area: first all Bizkaia, then Gipuzkoa, then France
        order = []
        for area in areas:
            order.append(f"{area}")
        
        # Prepare heatmap data with correct global order
        heatmap_data = df.set_index('row_id')[areas_all].loc[order]
        
        
        fig, ax = plot_connectivity_matrix(heatmap_data,age)
        ax.set_title(f"Mean connectivity matrix for {months[j]}")
    
        # Save as PNG 
        plt.tight_layout()
        plt.savefig(f"{plot_folder}/Connectivity_{age:02d}_mean_{mo:02d}.png", dpi=300, bbox_inches='tight')        




# In[4]  CONNECTIVITY MATRIX of YEARLY MEAN MISSING!!!!
# Vizualise connectivity matrix 
ages=[7,30,90]
mos = np.arange(1,13)
yrs = np.arange(1994,2025)

for i, age in enumerate(ages):
    M_file = f'{connectivity_folder}/Connectivity_matrix_{age}days_coast_previous_seeding5days.pkl'
    M = pd.read_pickle(M_file)
    # Group by month and seeding area and calculate mean across all years
    M_yearly_mean = M.groupby(['year', 'seeding_area']).mean(numeric_only=True)
    M_yearly_mean = M_yearly_mean.reset_index()
    
    for j, yr in enumerate(yrs):
        df = M_yearly_mean[M_yearly_mean['year']==yr]   #only select one year
        
        df['row_id'] = df['seeding_area']
        
        # Sort rows globally by seeding area: first all Bizkaia, then Gipuzkoa, then France
        order = []
        for area in areas:
            order.append(f"{area}")
        
        # Prepare heatmap data with correct global order
        heatmap_data = df.set_index('row_id')[areas_all].loc[order]
        
        
        fig, ax = plot_connectivity_matrix(heatmap_data,age)
        ax.set_title(f"Mean connectivity matrix for {yr}")
    
        # Save as PNG 
        plt.tight_layout()
        plt.savefig(f"{plot_folder}/Connectivity_{age:02d}_{yr}_mean.png", dpi=300, bbox_inches='tight') 


# In[5]  CONNECTIVITY MATRIX of ALL-TIME MEAN
# Vizualise connectivity matrix 
ages=[7,30,90]

for i, age in enumerate(ages):
    df = pd.read_csv(f"{connectivity_folder}/Connectivity_matrix_{age}days_all_mean_coast_previous_seeding5days.csv")
    #df = pd.read_csv(f"{connectivity_folder}/Connectivity_matrix_{age:02d}days_coast_previous_seeding5days.csv")
     
 #   # Create combined identifier for rows (month + seeding_area)
    df['row_id'] = df['seeding_area']
     
     # Sort rows globally by seeding area: first all Bizkaia, then Gipuzkoa, then France
    order = []
    for area in areas:
        order.append(f"{area}")
     
    # Prepare heatmap data with correct global order
    heatmap_data = df.set_index('row_id')[areas_all].loc[order]
    #heatmap_data[heatmap_data==0] = np.nan
    

    fig, ax = plot_connectivity_matrix(heatmap_data,age)
    ax.set_title("Mean connectivity matrix over 1994-2024")

    # Save as PNG 
    plt.tight_layout()
    plt.savefig(f"{plot_folder}/Connectivity_{age:02d}_mean_mean.png", dpi=300, bbox_inches='tight')
    
    
    
    
    
    

    
 