#!/usr/bin/env bash

#######   Andrea Favero,  26 January 2024  ##################################################
#  This bash script activates the venv, and starts the Cubotino_P.py script after the Pi boots
#  When the python script is terminated without errors (long button press), the Pi shuts down
#  (check notes below before uncommenting the "halt -p" command).
##############################################################################################

# activate the venv
source /home/pi/cubotino_pocket/src/.virtualenvs/bin/activate

# enter the folder with the main scripts
cd /home/pi/cubotino_pocket/src

# runs the robot main script, without or with arguments
python Cubotino_P.py
# python Cubotino_P.py --slow 10

# exit code from the python script
exit_status=$?

# based on the exit code there are three cases to be handled
if [ "${exit_status}" -ne 0 ];
then
    if [ "${exit_status}" -eq 2 ];
    then
        echo ""
        echo "Cubotino_P.py exited on request"
        echo ""
    else
        echo ""
        echo "Cubotino_P.py exited with error"
        echo ""
    fi
	
else
    echo ""
    echo "Successfully executed Cubotino_P.py"
    echo ""

    # ‘halt -p’ command shuts down the Raspberry pi
    # un-comment 'halt -p' command ONLY when the script works without errors
    # un-comment 'halt -p' command ONLY after making an image of the microSD
    halt -p

fi
