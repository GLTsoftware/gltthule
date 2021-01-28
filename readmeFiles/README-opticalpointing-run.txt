#################################################
Instruction on how to do optical pointing run
Last modified on 2017/Dec/22 by Hiroaki Nishioka
#################################################

Working directory
gltobscon:/home/obscon/pointing/

(0) Start RPC server on Opt/Cont PC and check the OT
Frist you need to start RPC server on OCC (OPC/Cont Computer).
ssh to OCC 

>ssh continuum@occ
 
On OCC, execute the python script "snap_svc3.py" under sitCodes 
>cd stiCodes
>python3 ./snap_svc3.py

Then check if you can take an image from gltobscon. Make sure 
you are under /home/obscon/pointing/work directory.

>./snapshot3.py 1 1 test 

The first "1" is the number of exposure, the second "1" is exposure time in sec.
Then make sure you got an image under "/OTimg" (for detail see section (2)(a) below.
You can use ds9 to check the image. Under /OTimg

>ds9 ***.fits

(1) Run full sky optical pointing script

To do optical pointing run, use the sript "azelstarControl-glt" 
that finds a target star, move the telescope to the target and 
take an optical image. The user needs to specify which az or el strip
to observe. To cover full sky, one example is (az=0,45,90,...,325),(el=20,40,60,80).
In this case the total number of stars will be ~150 in ~2 hours observation. 

Here is the usage of the script

For elevation direction at az=45 (-z 45) 
with a range of 5 deg (-w 5) 
from low elevation to high elevation (-d up, -d down for opposite)

>azelstarControl-glt -z 45 -w 5 -n 1 -d up

For azimuth direction at el=30 (-e 30)
with a range of 5 deg (-w 5)
along clock-wise direction (-d cw)

>azelstarControl-glt -e 30 -w 5 -n 1 -d cw

n is a maximum number of stars to observe in one section.

(2) After the observation 

(a) FITS images 
Images are saved in occ (Optical/Continuum Computer, 192.168.1.152)
under /home/continuum/OTimages/. After the observation please create a new directory 
to store the FITS images for current pointing run. Directory name consists of 6 numbers,
YYMMDD. For exapmle the observation on Dec 17 in 2017, the name is 171217. 
Please move all the FITS files to this directory.

(b) Pointing data 
During pointing run, the file named like "pointingData-2017-Dec-20"
is created. This is used for the analysis to derive pointing model. 
Please move this file to the directory "pointing_data" at the end of the day (in UT)
(if you move the data before the end of the day and another pointing run was 
done, then new pointingData file with the same name is created.)



