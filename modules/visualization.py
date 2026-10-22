#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 28 11:35:56 2025

@author: nsteiger
"""

def generate_outputs(o, plot_file, animation_file):
    #generate and save plot of last time step and animation
    o.plot(filename=plot_file,markersize=5,linewidth=2,fast=True)
    o.animation(filename=animation_file,buffer=0.1)