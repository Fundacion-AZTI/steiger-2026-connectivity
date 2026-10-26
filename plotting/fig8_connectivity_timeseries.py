#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jul 16 11:48:33 2026

@author: nsteiger
"""

import pandas as pd
import matplotlib.pyplot as plt






# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
connectivity_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/connectivity/trend'
out_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/connectivity'

# -- general settings-----
areas = ['fr_shelf', 'fr_slope', 'es_shelf', 'es_slope','deep']
areas_all = ['south','west','north','fr_shelf', 'fr_slope', 'es_shelf', 'es_slope','deep']




# In[1] Define different origin-seeding pairs

# Retention
# (seeding, origin)
pairs_retention = [
    (area, area) for area in areas
]

pairs_eastward = [
    ('west', 'deep'),
    ('west', 'fr_slope'),
    ('west', 'es_slope'),
    ('deep', 'fr_slope'),
    ('deep', 'fr_shelf'),
    ('deep', 'es_slope'),
    ('deep', 'es_shelf')    
]

# (seeding, origin)
pairs_westward = [
    ('fr_shelf', 'fr_slope'),
    ('fr_shelf', 'deep'),
    ('es_shelf', 'es_slope'),
    ('es_shelf', 'deep')   
]

# (seeding, origin)
pairs_northward = [
    ('south',   'es_slope'),
    ('south',   'es_shelf'),
    ('es_shelf',   'es_slope'),
    ('es_shelf',   'deep'),
    ('es_shelf',   'fr_slope'),
    ('es_shelf',   'fr_shelf')    
]

# (seeding, origin)
pairs_southward = [
    ('north',   'fr_shelf'),
    ('north',   'fr_slope'),   
    ('fr_shelf','es_shelf'),
    ('fr_shelf','es_slope'),
    ('deep',    'es_slope'),
    ('deep',     'es_shelf')
]
    
 

# -----
pairs_France = [
    ('deep',      'fr_slope'),
    ('deep',      'fr_shelf'),
    ('north',     'fr_slope'),
    ('north',     'fr_shelf'),
    ('es_shelf',  'fr_slope'),
    ('es_shelf',  'fr_shelf')
]

pairs_Spain = [
    ('south',     'es_slope'),
    ('south',     'es_shelf'),
    ('fr_shelf',  'es_slope'),
    ('fr_shelf',  'es_shelf'),
    ('deep',      'es_slope'),
    ('deep',      'es_shelf'),
    ('es_shelf',  'es_slope')
]

pairs_deep = [
    ('west',        'deep'),
    ('fr_shelf',    'deep'),
    ('es_shelf',    'deep')
]




    

# In[3]
# function for plotting each subplot
def plot_seasonal_cycle(k,pairs,col):
    for i, area in enumerate(pairs):
        seed = area[1]
        orig = area[0]
        
        txt=['(a)','(b)','(c)','(d)','(e)','(f)','(g)','(h)','(i)','(j)','(k)','(l)']
    
        # Extract series and timestamp
        M_filtered = M_sort[M_sort['seeding_area'] == seed][orig]
        M_time = M_sort[M_sort['seeding_area'] == seed]['date']
        
    
        # Combine into a temporary DataFrame
        df = pd.DataFrame({
            'date': M_time,
            'value': M_filtered
        })
    
        # Extract month (1–12)
        df['month'] = df['date'].dt.month
    
        # Compute seasonal cycle as monthly mean
        seasonal_cycle = df.groupby('month')['value'].mean()
        seasonal_std = df.groupby('month')['value'].std()
        
        # Plot seasonal cycle
        axs[k,j].plot(seasonal_cycle.index, seasonal_cycle.values, color=col(i),
                    label=f'{orig} → {seed}')
        
        axs[k,j].fill_between(seasonal_cycle.index,
                    seasonal_cycle - seasonal_std,
                    seasonal_cycle + seasonal_std,
                    color=col(i),
                    alpha=0.1)

        #if k==0:
        #    axs[k,j].set_title(f'{age} days simulation')
        if k==3:
            axs[k,j].set_xlabel("Seeding month")
            axs[k,j].set_xticks(range(1, 13))
            axs[k,j].set_xticklabels(['J','F','M','A','M','J','J','A','S','O','N','D'])
            axs[k,j].set_ylim([0,100])
        if j==0:
            axs[k,j].set_ylabel("Connectivity (%)")
        #if j==2:
        #    axs[k,j].legend(loc='upper right', fontsize=6)
        
        axs[k,j].text(1,80,txt[j+k*3])
            

        
        
    


# In[5]

import numpy as np


fig = plt.figure(figsize=(6.8, 6))


# ---- prepare axes ---------------------
# 3 columns of plots + 1 narrow legend column
gs = fig.add_gridspec(4, 4,width_ratios=[1, 1, 1, 0.1],wspace=0.15,hspace=0.15)

# data axes
axs = np.empty((4, 3), dtype=object)

for k in range(4):
    for j in range(3):
        if k == 0 and j == 0:
            axs[k, j] = fig.add_subplot(gs[k, j])
        else:
            axs[k, j] = fig.add_subplot(gs[k, j],sharex=axs[0, 0],sharey=axs[0, 0])

# legend axes (one per row)
legend_axes = []
for k in range(4):
    lax = fig.add_subplot(gs[k, 3])
    lax.axis("off")
    legend_axes.append(lax)


# loop over ages and plot
ages = [7, 30, 90]

for j, age in enumerate(ages):

    M_file = (f'{out_folder}/Connectivity_matrix_{age}days_coast_previous_seeding5days.pkl')
    M = pd.read_pickle(M_file)
    M = M.reset_index()

    # Create datetime from year and month
    M['date'] = pd.to_datetime(dict(year=M['year'].astype(int),
                                    month=M['month'].astype(int),
                                    day=1))
    M_sort = M.sort_values(['year','month'])
    
            
    plot_seasonal_cycle(0,pairs_retention,col = plt.colormaps['tab10'])

    plot_seasonal_cycle(1,pairs_France,col = plt.colormaps['tab20'])
    
    plot_seasonal_cycle(2,pairs_Spain,col = plt.colormaps['tab20'])
    
    plot_seasonal_cycle(3,pairs_deep,col = plt.colormaps['tab10'])



for k in range(4):
    for j in range(3):
        axs[k, j].label_outer()


for k in range(4):
    handles, labels = axs[k, 2].get_legend_handles_labels()
    legend_axes[k].legend(handles,labels,loc='center left',fontsize=7,frameon=False,handlelength=1.2,handletextpad=0.3,labelspacing=0.3,borderpad=0)

plt.rcParams.update({
    "font.size": 9,
    "axes.labelsize": 9,
    "xtick.labelsize": 8,
    "ytick.labelsize": 8
})

fig.subplots_adjust(wspace=0.03)
plt.tight_layout()
plt.savefig(f"{plot_folder}/Figure_8_connectivity_seasonal_cycle.png", dpi=300, bbox_inches='tight')

