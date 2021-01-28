######################################################################################
# This is a README for making tiltmeter measurements using the measureTilt.py script
# and analyzing the data
# prepared by: Jun Yi Koay
# last update: 29/08/18
######################################################################################

The measureTilt.py script moves the antenna to elevation 15 deg. It then moves the antenna 
from Az=5 deg to Az=335 deg in steps of 30 deg while keeping the El constant, and then 
back to Az = 5 deg. At each Az, it will wait 20s for the tiltmeter readings to stabilize,
then record the tiltmeter measurements in the file tiltReadings_XXXXXX_XXXXXX, where the Xs
represent the timestamp. This file is stored in:
hom/obscon/tilt/tiltdata/

Instructions:

1. cd into the folder: /home/obscon/tilt/ 

2. check to make sure that there is nobody using the antenna or in any of the cabins on the telescope!

3. run the script using the command: python3 measureTilt.py

4. run the fitTilt.py script as follows:

./fitTilt.py tiltdata/tiltReadings_XXXXXX_XXXXXX "figuretitle" y

This script will show the plots of the model fit to the tilt measurements, and print the tilt magnitude and 
direction on the screen. 

5. Record the tilt magnitude and direction on the Google doc for tiltmeasurements


########################################################################################
# Planned improvements:
# 1. combine the measureTilt and fitTilt scripts into one, so user only runs one single script
# 2. measureTilt current reads dsm temperatures and prints to screen but does not record it
#    to add more dsm parameters read and write them into a file together with tilt mag/direction.
#    This will enable us to plot tilt parameters against temperature etc
##########################################################################################

