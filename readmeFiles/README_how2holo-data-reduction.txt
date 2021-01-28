###
### How to reduce the holography data
###   Written by Satoki Matsushita (ASIAA)
###     with the instruction of T.K. Sridharan (CfA)
###       2019/10/28
###
###   Updated on 2020/02/27-03/06
###     by Nimesh Patel (CfA) & Satoki Matsushita (ASIAA)
###

obscon@gltobscon:~/holo$ cd regrid/

obscon@gltobscon:~/holo/regrid$ awk '{print $3,$2,$4,$5}' ../data/holoADC-AzEl-20191028_130410.txt > tmp


### Delete the first part that located at the bore sight
### and move to the scanning start point.
obscon@gltobscon:~/holo/regrid$ vi tmp


### Create the parameter file (only once per map size)
obscon@gltobscon:~/holo/regrid$ cp regrid_32x32_26oct19.prm regrid_64x64_28oct19.prm
obscon@gltobscon:~/holo/regrid$ vi regrid_64x64_28oct19.prm

  Nel Naz: grid number
    this case, 64 64
  AZstart: [center AZ] - [half of the gridding] x [grid size]
    this case, 230.2060 - (32 x 0.0114) = 229.8412
  ELstart: put exact starting EL of the first row of the raster scan.
    this case, 2.440


### Regridding
obscon@gltobscon:~/holo/regrid$ ./regridGLTxy tmp regrid_64x64_28oct19.prm > tmp1

obscon@gltobscon:~/holo/regrid$ grep : tmp1 > tmp2

obscon@gltobscon:~/holo/regrid$ vi tmp2

  Delete the first line: this case "pi: 3.141593"

obscon@gltobscon:~/holo/regrid$ awk '{print $4,$5,$8,$9}' tmp2 > holo-20191028_130410.rgrd


### Data check
> gnuplot
gnuplot> plot 'holo-20191028_130410.rgrd' u 1:2  <= El vs Az grid points
gnuplot> plot 'holo-20191028_130410.rgrd' u 1:3  <= El grid vs Amp
gnuplot> plot 'holo-20191028_130410.rgrd' u 2:3  <= Az grid vs Amp


### Pre-process
obscon@gltobscon:~/holo/regrid$ cp holo-20191028_130410.rgrd ../holis/preprocessing/rgin.dat

obscon@gltobscon:~/holo/regrid$ cd ../holis/preprocessing

obscon@gltobscon:~/holo/holis/preprocessing$ cp preprocess.prm preprocess32.prm

obscon@gltobscon:~/holo/holis/preprocessing$ vi preprocess.prm

  Size ninp of the input data file .......         64  <= change from 32 to 64.
  Size nout of the output data file.......         64  <= change from 32 to 64.

  ### Check out the "ADC offset, amplitude channel (counts)" parameter is zero.
  ADC offset, amplitude channel (counts)..          0.0

  ### If need to phase flip:
  vvm phase scaling (mv/deg)..............         -1.0  <= change from 1 to -1.

obscon@gltobscon:~/holo/holis/preprocessing$ ./preprocess


### Plot Maps
obscon@gltobscon:~/holo/holis/preprocessing$ ../../holografGLT
 Graphics device/type (? to see list, default /NULL): /xw  <= input X window
 Name for the input data array?
ampout.dat  <= input this file name.
 Name for the input data array?
phaseout.dat  <= input this file name.
 Dimension N of the input N by N data array (less than or equal to 512) ?
64  <= input grid size.
 Dimension N of the input N by N data array (less than or equal to 512) ?
64  <= input grid size.
 The maximum value in the data file is  0.969860017    
 The minimum value in the data file is   1.99999996E-02
 OK1
 OK2
 Please specify value for WHITE (default=maximum):

 Please specify value for BLACK (default=minimum):

 white=  0.969860017    
 black=   1.99999996E-02
 NOTE THAT THE BLACK AND WHITE ON THE SCREEN
 MAY BE REVERSED FROM THE SPECIFIED VALUE (BUT
 WILL BE CORRECT FOR A POSTSCRIPT PRINTOUT) !!!
 Wedge label1?
amp  <= input the label for the greyscale.
 Want to draw panel boundaries(1/0)?
0  <= Not drawing panel boundaries.
 The maximum value in the data file is   3.11865067    
 The minimum value in the data file is  -3.36110449    
 Please specify value for WHITE (default=maximum):

 Please specify value for BLACK (default=minimum):

 white=   3.11865067    
 black=  -3.36110449    
 Wedge label2?
phase  <= input the label for the greyscale.
 Produce postscript output (y/n, default=n)?

 Type <RETURN> for next page: 
   0.00000000               0           0   4.58404724E+30   0.00000000    


### Save data
obscon@gltobscon:~/holo/holis/preprocessing$ cp ampout.dat holo-20191028_130410.amp
obscon@gltobscon:~/holo/holis/preprocessing$ cp phaseout.dat holo-20191028_130410.pha


### In case of 96x96 map, need to pad zeros to make 128x128 map, which can
### be processed by the following processes that needs 2^n.

obscon@gltobscon:~/holo/holis/preprocessing$ ./96to128.pl holo-20200226_184954-calib

(This will overwrite the previous ampout.dat and phaseout.dat with padded ones).


### FFT
obscon@gltobscon:~/holo/holis/preprocessing$ cp ampout.dat ../inversion/aber2/
obscon@gltobscon:~/holo/holis/preprocessing$ cp phaseout.dat ../inversion/aber2/

obscon@gltobscon:~/holo/holis/preprocessing$ cd ../inversion/aber2/

####### IMPORTANT!!! #######
### If you run 96to128.pl as above, keep the N value to 128 in the .prm
### files below!
############################

obscon@gltobscon:~/holo/holis/inversion/aber2$ vi panelplt.prm

  Dimension of the phase data array.......         64  <= Change from 32 to 64.

obscon@gltobscon:~/holo/holis/inversion/aber2$ vi withphase_aber.prm

  Size N of the N by N data file .........         64  <= Change from 32 to 64.

obscon@gltobscon:~/holo/holis/inversion/aber2$ ./holis_aber2
 Which algorithm you choose to use(1 for phase cohere  2 for misell phase recovery, 3 for global fitting) ?
1  <= Phase coherence holography.
 Use with-phase holography algorithm
 (You must first fill out "withphase.prm")
  
 -- Reading parameters from "withphase.prm" --
  
 Far field amplitude file name =ampout.dat     
 Far field phase file name =phaseout.dat   
 Aperture field amplitude file name =Ea.dat         
 Aperture field phase file name =Ep.dat         
 Residual aperture phase file name =Epr.dat        
 umResidual aperture phase file name:Epr_um.dat     
 um aperture amp file name =Ea_um.dat      
 um aperture phase file name =Ep_um.dat      
 Size N of the N by N array =         128
 Nyquist sampling rate =  0.75209999999999999     
 Distance of the transmitter (meters)=   3095.0000000000000     
 Observing Frequency (GHz) =   94.500000000000000     
 Samping intervel in the far field (arcsec) =   41.039999999999999     
 Diameter of the primary mirror (m) =   12.000000000000000     
 Diameter of the secondary mirror (m) =  0.75000000000000000     
 Focal length of the primaray (m) =   4.7999999999999998     
 Magnification of the Cassegrain system =   20.000000000000000     
 Name of phase diffraction file =diff512.dat    
 Number of the large scale fitting parameter =           8
 Near field correction =            1
 Defocus correction =    1.0180000000000000E-002
 Outer dia for masking =    11.500000000000000     
 Inner dia for masking =    2.0000000000000000     
 half-width for quadrupod masking =   0.10000000000000001     
 maskfile name = mask32.dat     
 fitting function i=           1  ON/OFF           1
 fitting function i=           2  ON/OFF           1
 fitting function i=           3  ON/OFF           1
 fitting function i=           4  ON/OFF           1
 fitting function i=           5  ON/OFF           0
 fitting function i=           6  ON/OFF           0
 fitting function i=           7  ON/OFF           1
 fitting function i=           8  ON/OFF           1
 do you want to read in an unwrapped                    file(tk.dat) (1/0)?
0    
  
 rms before the phasefit =  0.34322320468441836        radian
 phasefit_aber2 call
 coef(1)=   2.0775905668952577         ! constant offset
 coef(2)=  -6.3856828793964690E-003    ! tilt in x direction
 coef(3)=   3.7354613458438781E-003    ! tilt in y direction
 coef(4)=  -8.7787385216874278E-002    ! defocus in mm
 coef(5)=   6.1623413006199049E-018    ! astigmatism-45 term
 coef(6)=   0.0000000000000000         ! astigmatism term
 coef(7)=  -1.6631295416702210E-003    ! coma-x term
 coef(8)=   3.9979315113674335E-005    ! coma-y term
 chisq=   247.76128656433022     
 rms after the phasefit =  0.20368395734970393        radian
Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG


### Plot Maps
obscon@gltobscon:~/holo/holis/inversion/aber2$ ../../../holografGLT
 Graphics device/type (? to see list, default /NULL): /xw
 Name for the input data array?
Ea_um.dat  <= Electric field amplitude
 Name for the input data array?
Ep_um.dat  <= Electric field phase
 Dimension N of the input N by N data array (less than or equal to 512) ?
128  <= input grid size.
 Dimension N of the input N by N data array (less than or equal to 512) ?
128  <= input grid size.
 The maximum value in the data file is   9.57133770E-02
 The minimum value in the data file is   0.00000000    
 OK1
 OK2
 Please specify value for WHITE (default=maximum):
0.07
 Please specify value for BLACK (default=minimum):

 white=   7.00000003E-02
 black=   0.00000000    
 NOTE THAT THE BLACK AND WHITE ON THE SCREEN
 MAY BE REVERSED FROM THE SPECIFIED VALUE (BUT
 WILL BE CORRECT FOR A POSTSCRIPT PRINTOUT) !!!
 Wedge label1?
Illumination
 Want to draw panel boundaries(1/0)?
1  <= Draw panel boundaries.
 panels!
  
 - Reading parameters from "panelplt.prm" -
  
 Dimension of the phase data file=         128
 Radius of the first ring of nodes =  0.375000000    
 Radius of the second ring of nodes =   1.26499999    
 Radius of the third ring of nodes =   1.82000005    
 Radius of the fourth ring of nodes =   2.60500002    
 Radius of the fifth ring of nodes =   3.22000003    
 Radius of the sixth ring of nodes =   4.03999996    
 Radius of the seventh ring of nodes =   4.78000021    
 Radius of the eighth ring of nodes =   5.43499994    
 Radius of the ninth ring of nodes =   6.00000000    
 Number of panels in the first ring=          12
 Number of panels in the second ring=          12
 Number of panels in the third ring=          24
 Number of panels in the fourth ring=          24
 Number of panels in the fifth ring=          48
 Number of panels in the sixth ring=          48
 Number of panels in the seventh ring=          48
 Number of panels in the eighth ring=          48
 Distance of the screws to panel edge =   5.00000007E-02
 Focal length of the primary mirror =   4.80000019    
 Diameter of the primary mirror =   12.0000000    
 Diameter of the secondary mirror =  0.750000000    
 Nyquist sampling rate =  0.750000000    
 Radial margin on the panel for masking   9.99999978E-03
 Theta margin on the panel for masking   4.00000019E-03
 Theta offset from elevation axis   4.00000019E-03

 The maximum value in the data file is   3.14148450    
 The minimum value in the data file is  -3.14114761    
 Please specify value for WHITE (default=maximum):

 Please specify value for BLACK (default=minimum):

 white=   3.14148450    
 black=  -3.14114761    
 Wedge label2?
Surface Error
 panels!


obscon@gltobscon:~/holo/holis/inversion/aber2$ cp Ea_um.dat holo-20200226_184954-calib.Ea
obscon@gltobscon:~/holo/holis/inversion/aber2$ cp Ep_um.dat holo-20200226_184954-calib.Ep
obscon@gltobscon:~/holo/holis/inversion/aber2$ cp Epr_um.dat holo-20200226_184954-calib.Epr
obscon@gltobscon:~/holo/holis/inversion/aber2$ cp holis.log holo-20200226_184954-calib.log


In holis.log,
  "rms after the phasefit =  0.45460512733561020        radian"
is the final rms in radian (multiply lambda/4pi = 300000/94.5/4pi = 252.6 makes in micron).


### In case there is phase wrapped feature in the Ep_um.dat map,
### do phase unwrapping.  Do this procedure just after the above
### procedures, since it uses "Ep.dat" that produced by "./holis".

obscon@gltobscon:~/holo/holis/inversion/aber2$ ../../unwrap/unwrap Ep.dat tk.dat 128
  <= "Ep.dat" is the file produced by previous "./holis".
  <= "tk.dat" is the file that includes the phase unwrap information.
     The filename must be this.
  <= "128" is the pixel size of the map.
../unwrap/unwrap	Ep.dat	tk.dat
Give limit:3.5  <= "3.5" is step in radian. Give this value.
Ask (1/0)?0     <= "0" will do all the phase unwrapping automatically.
                   In case of "1", the program asks every phase unwrapping.

### Re-run "./holis_aber2".
obscon@gltobscon:~/holo/holis/inversion/aber2$ ./holis_aber2
 Which algorithm you choose to use(1 for phase cohere  2 for misell phase recovery, 3 for global fitting) ?
1  <= Phase coherence holography
 Use with-phase holography algorithm
 (You must first fill out "withphase.prm")
  
 -- Reading parameters from "withphase.prm" --
  
 Far field amplitude file name =ampout.dat     
 Far field phase file name =phaseout.dat   
 Aperture field amplitude file name =Ea.dat         
 Aperture field phase file name =Ep.dat         
 Residual aperture phase file name =Epr.dat        
 umResidual aperture phase file name:Epr_um.dat     
 um aperture amp file name =Ea_um.dat      
 um aperture phase file name =Ep_um.dat      
Size N of the N by N array =         128
 Nyquist sampling rate =  0.75209999999999999     
 Distance of the transmitter (meters)=   3095.0000000000000     
 Observing Frequency (GHz) =   94.500000000000000     
 Samping intervel in the far field (arcsec) =   41.039999999999999     
 Diameter of the primary mirror (m) =   12.000000000000000     
 Diameter of the secondary mirror (m) =  0.75000000000000000     
 Focal length of the primaray (m) =   4.7999999999999998     
 Magnification of the Cassegrain system =   20.000000000000000     
 Name of phase diffraction file =diff512.dat    
 Number of the large scale fitting parameter =           8
 Near field correction =            1
 Defocus correction =    1.0180000000000000E-002
 Outer dia for masking =    11.500000000000000     
 Inner dia for masking =    2.0000000000000000     
 half-width for quadrupod masking =   0.10000000000000001     
 maskfile name = mask32.dat     
 fitting function i=           1  ON/OFF           1
 fitting function i=           2  ON/OFF           1
 fitting function i=           3  ON/OFF           1
 fitting function i=           4  ON/OFF           1
 fitting function i=           5  ON/OFF           0
 fitting function i=           6  ON/OFF           0
 fitting function i=           7  ON/OFF           1
 fitting function i=           8  ON/OFF           1
 do you want to read in an unwrapped                    file(tk.dat) (1/0)?
1  <= Now type "1" to phase unwrap using "tk.dat".
  
 rms before the phasefit =  0.34322320130902773        radian
 phasefit_aber2 call
 coef(1)=   2.0775905642766506         ! constant offset
 coef(2)=  -6.3856829007902845E-003    ! tilt in x direction
 coef(3)=   3.7354606981660253E-003    ! tilt in y direction
 coef(4)=  -8.7787384784518294E-002    ! defocus in mm
 coef(5)=   6.1623414841586913E-018    ! astigmatism-45 term
 coef(6)=   0.0000000000000000         ! astigmatism term
 coef(7)=  -1.6631294774127334E-003    ! coma-x term
 coef(8)=   3.9979484314372601E-005    ! coma-y term
 chisq=   247.76128919511481     
 rms after the phasefit =  0.20368395843108472        radian
Note: The following floating-point exceptions are signalling: IEEE_INVALID_FLAG


### Plot Maps
obscon@gltobscon:~/holo/holis/inversion/aber2$ ../../../holografGLT
 Graphics device/type (? to see list, default /NULL): /xw
 Name for the input data array?
Ep_um.dat  <= Original phase wrapped map.
 Name for the input data array?
Epr.dat    <= Phase unwrapped map.
 Dimension N of the input N by N data array (less than or equal to 512) ?
128
 Dimension N of the input N by N data array (less than or equal to 512) ?
128
 The maximum value in the data file is   3.14153981    
 The minimum value in the data file is  -3.14158821    
 OK1
 OK2
 Please specify value for WHITE (default=maximum):

 Please specify value for BLACK (default=minimum):
1
 white=   3.14153981    
 black=   1.00000000    
 NOTE THAT THE BLACK AND WHITE ON THE SCREEN
 MAY BE REVERSED FROM THE SPECIFIED VALUE (BUT
 WILL BE CORRECT FOR A POSTSCRIPT PRINTOUT) !!!
 Wedge label1?
Phase Wrapped
 Want to draw panel boundaries(1/0)?
1
 panels!
  
 - Reading parameters from "panelplt.prm" -
  
 Dimension of the phase data file=         128
 Radius of the first ring of nodes =  0.375000000    
 Radius of the second ring of nodes =   1.26499999    
 Radius of the third ring of nodes =   1.82000005    
 Radius of the fourth ring of nodes =   2.60500002    
 Radius of the fifth ring of nodes =   3.22000003    
 Radius of the sixth ring of nodes =   4.03999996    
 Radius of the seventh ring of nodes =   4.78000021    
 Radius of the eighth ring of nodes =   5.43499994    
 Radius of the ninth ring of nodes =   6.00000000    
 Number of panels in the first ring=          12
 Number of panels in the second ring=          12
 Number of panels in the third ring=          24
 Number of panels in the fourth ring=          24
 Number of panels in the fifth ring=          48
 Number of panels in the sixth ring=          48
 Number of panels in the seventh ring=          48
 Number of panels in the eighth ring=          48
 Distance of the screws to panel edge =   5.00000007E-02
 Focal length of the primary mirror =   4.80000019    
 Diameter of the primary mirror =   12.0000000    
 Diameter of the secondary mirror =  0.750000000    
 Nyquist sampling rate =  0.750000000    
 Radial margin on the panel for masking   9.99999978E-03
 Theta margin on the panel for masking   4.00000019E-03
 Theta offset from elevation axis   4.00000019E-03

 The maximum value in the data file is   10000.0000    
 The minimum value in the data file is  -1.83371067    
 Please specify value for WHITE (default=maximum):
0.7
 Please specify value for BLACK (default=minimum):
-0.7
 white=  0.699999988    
 black= -0.699999988    
 Wedge label2?
Phase Unwrapped
 panels!

obscon@gltobscon:~/holo/holis/inversion/aber2$ cp Epr.dat holo-20200226_184954-calib.Epr
obscon@gltobscon:~/holo/holis/inversion/aber2$ cp holis.log holo-20200226_184954-calib.log


#######
### Note from TK (2020/03/04):
###
### If the above phase unwrap procedure does not completely get rid of the wrap: 
###
###  Often phase wrapping can be overcome by experimenting with the near field focus
### correction amount. We put the value corresponding to the actual setting during
### the map, one can move this around which can move the phase warp boundary outside
### the dish and the fitting gets back the correction for this wrong setting.
### The signature of focus induced phase wrap is circular symmetry, or an arc like
### transition line.
###
###  If the phase wrapping is due to pointing - a large gradient across the dish
### results in wrapping some where, the signature for this is a straightish  wrap
### boundary. This can be curved when combined with focus. If a dominant gradient
### feature is seen, the regrid parameters can be changed to recenter the extracted
### map (only possible for azimuth). If in elevation, the bore-sight co-ordinates
### need revision.  
###
###  If none of this solves the problem, there is an interactive unwrap - a video
### game like thing, where you click the pixel where you think a wrap is occurring
### and it unwraps it. I did not have to go to this step in any of the data, I am
### not even sure a running compiled version of int_unwrap is present in the GLT
### installation.
###
###  If we are having to struggle with wrapping too much, it is usually due to bad
### data and the focus should be solving that problem.  
#######


### Map/Data Averaging
obscon@gltobscon:~/holo/holis/inversion/aber2$ ../ave.pl 
number of files?
3    <= Put how many files to be averaged.
number of rows?
128  <= Put how many pixels these files have.
filename No.0
holo-20200226_184954-calib_SM  <= Filename without extension. Program automatically reads .Ea and .Epr files.
filename No.1
holo-20200302_133151-calib_SM    
filename No.2
holo-20200302_144704-calib_SM    
Epr.dat and Ea.dat were created!
Done!

obscon@gltobscon:~/holo/holis/inversion/aber2$ cp Ea.dat holo-20200226_184954-20200302_133151-144704_ave3.Ea
obscon@gltobscon:~/holo/holis/inversion/aber2$ cp Epr.dat holo-20200226_184954-20200302_133151-144704_ave3.Epr


### Calculate Surface RMS
obscon@gltobscon:~/holo/holis/inversion/aber2$ cp holo-20200226_184954-20200302_133151-144704_ave3.Epr tk.dat
obscon@gltobscon:~/holo/holis/inversion/aber2$ ./holis_aber2
 Which algorithm you choose to use(1 for phase cohere  2 for misell phase recovery, 3 for global fitting) ?
1  <= Phase coherence holography
 Use with-phase holography algorithm
 (You must first fill out "withphase.prm")
  
 -- Reading parameters from "withphase.prm" --
  
 Far field amplitude file name =ampout.dat     
 Far field phase file name =phaseout.dat   
 Aperture field amplitude file name =Ea.dat         
 Aperture field phase file name =Ep.dat         
 Residual aperture phase file name =Epr.dat        
 umResidual aperture phase file name:Epr_um.dat     
 um aperture amp file name =Ea_um.dat      
 um aperture phase file name =Ep_um.dat      
 Size N of the N by N array =         128
 Nyquist sampling rate =  0.75209999999999999     
 Distance of the transmitter (meters)=   3095.0000000000000     
 Observing Frequency (GHz) =   94.500000000000000     
 Samping intervel in the far field (arcsec) =   41.039999999999999     
 Diameter of the primary mirror (m) =   12.000000000000000     
 Diameter of the secondary mirror (m) =  0.75000000000000000     
 Focal length of the primaray (m) =   4.7999999999999998     
 Magnification of the Cassegrain system =   20.000000000000000     
 Name of phase diffraction file =diff512.dat    
 Number of the large scale fitting parameter =           8
 Near field correction =            1
 Defocus correction =    1.0180000000000000E-002
 Outer dia for masking =    11.500000000000000     
 Inner dia for masking =    2.0000000000000000     
 half-width for quadrupod masking =   0.10000000000000001     
 maskfile name = mask32.dat     
 fitting function i=           1  ON/OFF           1
 fitting function i=           2  ON/OFF           1
 fitting function i=           3  ON/OFF           1
 fitting function i=           4  ON/OFF           1
 fitting function i=           5  ON/OFF           0
 fitting function i=           6  ON/OFF           0
 fitting function i=           7  ON/OFF           1
 fitting function i=           8  ON/OFF           1
 do you want to read in an unwrapped                    file(tk.dat) (1/0)?
1  <= If you type 1 here, then the rms calculation below will be the surface rms.
  
 rms before the phasefit =  0.18019804798094222        radian
 phasefit_aber2 call
 coef(1)=  -4.6283865557847993E-004    ! constant offset
 coef(2)=  -5.3831422550622144E-006    ! tilt in x direction
 coef(3)=  -1.8946362715339664E-005    ! tilt in y direction
 coef(4)=   1.2700971410394524E-003    ! defocus in mm
 coef(5)=   1.8131627736175458E-020    ! astigmatism-45 term
 coef(6)=   0.0000000000000000         ! astigmatism term
 coef(7)=   4.7025984326775848E-006    ! coma-x term
 coef(8)=   8.1304412169226270E-006    ! coma-y term
 chisq=   193.91755794309844     
 rms after the phasefit =  0.18019746087763805        radian
   <= So, the averaged surface rms = 0.180197 x 252.6 = 45.5 micron.

