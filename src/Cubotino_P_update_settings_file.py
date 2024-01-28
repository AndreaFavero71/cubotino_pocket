#!/usr/bin/env python
# coding: utf-8

"""
######################################################################################################################
# Andrea Favero 26 January 2024
# 
# Little script adding to Cubotino_P_settings.txt the new parameters, eventually added after first release
# This script relates to CUBOTino Pocket, a small and simple Rubik's cube solver robot 3D printed
#
######################################################################################################################
"""

import os.path, pathlib, json                                 # libraries needed for the json, and parameter import

def update_settings_file(fname, settings):
    """Function to check if the existing fname (Cubotino_P_settings.txt) has all the parameters that were instroduced after firt release.
        This will allow every Makers to 'git pull' the updates while pre-serving personal settings (*_settings.txt to gitignore)."""

    settings_keys = settings.keys()
    any_change = False
    
#     if 'new_parameter' not in settings_keys:
#         settings['new_parameter']='value'
#         any_change = True

    if any_change:
        print('\nOne time action: Adding new parameters to the Cubotino_P_settings.txt')
        print('Action necessary for compatibility with the latest downloaded version \n')
        with open(fname, 'w') as f:
            f.write(json.dumps(settings, indent=0))   # content of the updated setting is saved
    
    return settings



def update_srv_settings_file(fname, settings):
    """Function to check if the existing fname (Cubotino_P_servo_settings.txt) has all the parameters that were instroduced after firt release.
        This will allow every Makers to 'git pull' the updates while pre-serving personal settings (*_settings.txt to gitignore)."""

    settings_keys = settings.keys()
    any_change = False
    
#     if 'new_parameter' not in settings_keys:
#         settings['new_srv_parameter']='srv_value'
#         any_change = True

    if any_change:
        print('\nOne time action: Adding new parameters to the Cubotino_P_servo_settings.txt')
        print('Action necessary for compatibility with the latest downloaded version \n')
        with open(fname, 'w') as f:
            f.write(json.dumps(settings, indent=0))   # content of the updated setting is saved
    
    return settings
    