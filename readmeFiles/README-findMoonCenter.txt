############################################################
Last modified 2018/Jan/10
############################################################

############################################################
Brief Description
############################################################

The findMoonCenter.py program determines the position of the 
Moon center based on azimuth/elevation scans. It outputs the 
Az/El offset value of the scan corresponding to the center 
of the Moon. This program may be helpful when using the Moon 
for pointing and focusing observations.

The current version uses two methods to estimate the offset 
value of the Moon center and prints out both:

Method A: 
the program finds the left and right edges of the Moon at 
1/5 the peak power, then finds the centre position between 
these two edges.

Method B: 
the program determines the 'derivative' (or slope) between 
each pair of successive points, then selects the position of 
maximum and minimum slope as the two Moon edges, which is 
then used to determine the centre.


############################################################
Instructions
############################################################

1. To run the program, type:

python3 findMoonCenter.py filename scantype

'filename' is the name of the file containing the offset scan data. 
'scantype' should be 'el' for an elevation scan, or 'az' for an azimuth scan.

E.g.:
python3 findMoonCenter.py contData_180108_080810 az

2. A figure will appear: 
the top panel shows Continuum Output 1 vs Offset (red for method A, black for method B)
the bottom panel shows the slope from Method B vs Offset 
Estimated Offset values of the Moon center is printed on the terminal

3. To stop the program, close the figure.

############################################################
Important Notes
############################################################

1. Method A currently does not account for an additional 
slope in continuum output power due to sky noise; this affects 
mainly elevation scans. This will be updated in future versions.

2. Method B currently is affected by slow data readout, such 
that there are successive scans having the same offset value. 
This leads to a division by 0 when calculating the slope. At 
present, the workaround is to let (offset2 - offset1) be equal 
to the mean offset from the entire az/el scan.

3. This program has not been tested vigorously, but it seems 
that Method A may be better in the initial stages when the 
focussing is not very good. Method B may perform better when 
better focused. I am still working to improve the algorithms.



