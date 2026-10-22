#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 31 11:32:01 2025

@author: nsteiger
"""

def create_file_names(res,dt,yr,mo,sim_folder,sim_name=None):
    #file name with relative path for output and figure files
    if sim_name is not None:
        fname = f'Connectivity_ibi_backward_{res:.2f}deg_{dt}s_{yr}_{mo:02d}_{sim_name}' #modify this according to simulation
    else:
        fname = f'Connectivity_ibi_backward_{res:.2f}deg_{dt}s_{yr}_{mo:02d}'
    
    out_file = f'{sim_folder}/output/{fname}.nc'
    plot_file = f'{sim_folder}/figures/{fname}.png'
    animation_file = f'{sim_folder}/figures/{fname}.gif'
    seeding_file = f'{sim_folder}/ini_pos_CONNECTIVITY_IBI_{res:.2f}deg.dat'
    

    print(out_file)
    
    return out_file, plot_file, animation_file, seeding_file