#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 30 12:32:51 2025

@author: nsteiger
"""
import importlib.util
import os

# Load config dynamically from a given simulation folder

def load_config(sim_folder,config_file='config.py'):
    # config_path = os.path.join(sim_path,'config.py')
    config_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', sim_folder, config_file))  #from this script ../sim_folder/config.py
    spec = importlib.util.spec_from_file_location("config", config_path)
    config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(config)
    return config
