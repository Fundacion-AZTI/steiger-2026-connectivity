#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 15:09:18 2026

@author: nsteiger
"""

# In[1]


import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable



# --- paths ----
bathy_file = '/data2/BIOCEAN5D/Data/GEBCO_01_Oct_2025/gebco_2025_n50.6_s38.9_w-13.1_e-1.0.nc'
plot_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/paper/figures/'
connectivity_folder = '/data2/BIOCEAN5D/Connectivity/2026_01_08_seeding5days_1993-2024/results/connectivity/trend'


# -- general settings-----
areas = ['fr_shelf', 'fr_slope', 'es_shelf', 'es_slope','deep']
areas_all = ['south','west','north','fr_shelf', 'fr_slope', 'es_shelf', 'es_slope','deep']


# In[2]
# Vizualise connectivity matrix - ALL AGES IN ONE FIGURE
ages=[7,30,90]
txt = ['(a)','(b)','(c)']


# Create plot
fig, axs = plt.subplots(1, 3, figsize=(6.8,2.5), sharex=True, sharey=True)
w = axs[0].get_position().width
h = axs[1].get_position().height-0.15

for i, age in enumerate(ages):
    df_trend = pd.read_csv(f"{connectivity_folder}/Connectivity_matrix_{age}days_trend_deseasoned_coast_previous_seeding5days.csv")
    df_pval= pd.read_csv(f"{connectivity_folder}/Connectivity_matrix_{age}days_pval_deseasoned_coast_previous_seeding5days.csv")
    
 #   # Create combined identifier for rows (month + seeding_area)
    df_trend['row_id'] = df_trend['seeding_area']
    df_pval['row_id'] = df_pval['seeding_area']
    
    # Sort rows globally by seeding are
    order = []
    for area in areas:
        order.append(f"{area}")
    
    # Prepare heatmap data with correct global order
    heatmap_data = df_trend.set_index('row_id')[areas_all].loc[order]*1000
    cond_data = df_pval.set_index('row_id')[areas_all].loc[order]
    
  # mask significance
    pval005 = (cond_data.values < 0.05) & (cond_data.values > 0.01)
    pval001 = cond_data.values < 0.01
    



    if i==len(ages)-1:
        #divider = make_axes_locatable(axs[i])
        #cax = divider.append_axes("right", size="4%", pad=0.05)  # ← decrease pad
        hm = sns.heatmap(heatmap_data, cmap="RdBu_r", vmin=-0.02*1000, vmax=0.02*1000, annot=True, fmt=".0f", ax=axs[i], cbar=False)
        #hm = sns.heatmap(heatmap_data, cmap="viridis", vmin=0, vmax=100, annot=True, fmt=".0f", ax=axs[i], cbar_ax=cax, cbar_kws={'label':'Connectivity [%]'})
    else:
        hm = sns.heatmap(heatmap_data, cmap="RdBu_r", vmin=-0.02*1000, vmax=0.02*1000,  annot=True, fmt=".0f", ax=axs[i], cbar=False)

    # Annotate per cell, bold where mask is True
    nrows, ncols = heatmap_data.shape
    for j in range(nrows):
        for k in range(ncols):
            val = heatmap_data.iat[j, k]
            if pd.isna(val):
                continue  # skip NaNs
            text = format(val,".0f")
            is_95 = bool(pval005[j, k])
            is_99 = bool(pval001[j, k])
            kw = {
                "ha": "center",
                "va": "center",
                "fontweight": "bold" if is_99 else "normal",
                "color": "black" if is_95 else "black" if is_99 else "gray",
                "fontstyle": "italic" if is_95 else "italic" if is_99 else "normal",
            }
            # Heatmap cells are centered at (j+0.5, i+0.5)
            axs[i].text(k + 0.5, j + 0.5, text, **kw)


    # create a standalone colorbar axis
    cax = fig.add_axes([0.40, 0.9, w, 0.03])
    
    cb = fig.colorbar(hm.collections[0],cax=cax,orientation="horizontal",label="Connectivity [%]")
    
    cb.ax.xaxis.set_ticks_position('top')
    cb.ax.xaxis.set_label_position('top')
    cb.set_label('Connectivity trend [x 0.001 %/ month]')
    cb.outline.set_visible(False)


    #axs[i].set_title(f"Connectivity matrix for {age:02d} days")
    axs[i].set_xlabel(f"{txt[i]} Origin subareas ({age:02d} days)")
    if i==0:
        axs[i].set_ylabel("Seeding subarea")
    else:
        axs[i].set_ylabel(" ")
    axs[i].tick_params(axis='y', labelrotation=60)
    axs[i].tick_params(axis='x', labelrotation=90)
    
    # Vertical line between column 3 and 4
    axs[i].axvline(x=3, color='gray', linewidth=2)

    # --- Highlight diagonal ---
    for l in range(heatmap_data.shape[0]):
        axs[i].add_patch(plt.Rectangle((l+3, l), 1, 1, fill=False,
                                   edgecolor='gray', linewidth=2))
    
    
    # Draw a box around the heatmap
    for spine in axs[i].spines.values():
        spine.set_visible(True)
        spine.set_linewidth(0.5)   # thickness of the box
        spine.set_color("gray") # color of the box
        
    plt.rcParams.update({
        "font.size": 8,
        "axes.labelsize": 8,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8
    })
   

  
for ax in axs:
    pos = ax.get_position()
    ax.set_position([pos.x0, pos.y0, pos.width, h])
    

    
fig.subplots_adjust(wspace=0.06)
plt.savefig(f"{plot_folder}/Figure_9_Connectivity_trend.png", dpi=300, bbox_inches='tight')