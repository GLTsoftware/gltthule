##
## 5-points spectral pointing, data taking & errors derivation
##

=== Preparation for Spectrometer PC ===

- Login the spectrometer PC as root@192.168.1.25

- If necessary (ex. not using the spectrometer for sometime, or after power outage), manually execute mmcm calibration and full ROACH initialization:

$ cd /data/glt/
$ python2.7 /data/glt/adc_cal/ioDelayIQSetup.py 192.168.50.15
$ python2.7 /data/glt/glt_init.py glt_32k.conf -a -v
$ python2.7 /data/glt/glt_init.py glt_32k_1.conf -v -p 

- check if there is a previous server instance; if yes, kill it.
$ ps aux | grep -i ctrl_rpc_server

- run the server, and keep this terminal for monitoring
$ source /data/miniconda3/bin/activate spectctl
(spectctl) $ python3 /home/ACC/ctrl_rpc_server.py


#######
# New (April 05, 2018)
- Check and edit acc_len in /data/glt/glt_32k.conf
  acc_len = 2000  # original value, 32msec integration period
  acc_len = 20000 # 320msec integration period
#######

=== Preparation for Obscon ===

- mount Spectrometer PC filesystem via GVFS/SFTP
On Ubuntu Desktop, launch the "Files" app and use "Connect to Server" at the left panel. Select the connection history item to 192.168.1.25. A symbolic link $HOME/pointing/spectrometer_glt now shall point to the remote data dir SpectPC:/data/glt.

- Make the antenna start tracking the desired line source. If there are presets for azoff and/or eloff, also enter now.


=== Obtain Data ===

- For 5-on-5-off scan, use the script "l5pt_client.py"; otherwise, for 1-off-5-on, use "l5pt_client-1f5n.py". 

- For a special need of 1-on-1-off scan, replace the line "off_label = ['Center', 'Az+', 'Az-', 'El+', 'El-']" with "off_label = ['Center']" in "l5pt_client.py".

$ cd $HOME/pointing/
$ python3 l5pt_client.py <Int_Sec> <Offset_Arcsec>  
or
$ python3 l5pt_client-1f5n.py <Int_Sec> <Offset_Arcsec>  
# integration time at each offset, and offset separation (usually equal to half-beam)

- Once done, a meta file as "spect5Pt_yyMMDD_hhmmss" will be generated.

#######
# New
For focusing in Z-direction,
Z will shift by -2ZStep, -ZStep, 0, Ztep, -2ZStep from the original position.
$./l5z_client.py <Int_Sec> <ZStep_um>
or
$./l5z_client-1f5n.py <Int_Sec> <ZStep_um>
  ZStep = 1000 for 86GHz
  ZStep = 500 for 230GHz
#######

=== Analyze the Data and Derive the Pointing Errors ===
# Old 
1. Copy the spectra data from the spectrometer PC to Obscon
$ head -n 1 spect5Pt_yyMMDD_hhmmss	
# find the two h5 files, whose time stamps usually differ by 1 sec.

2. Copy h5 file
$ cp spectrometer_glt/2018_Mar_07_21_18_5[67].glt.h5 .		# for example

$ python3 l5pt_analysis.py spect5Pt_yyMMDD_hhmmss bin_num
or
$ python3 l5pt_analysis-1f5n.py spect5Pt_yyMMDD_hhmmss bin_num
# Once again, for 1-off-5-on, use "l5pt_analysis-1f5n.py" instead.

##############
# New (April 5, 2018)
$./l5pt_analysis_lu.py spect5Pt_yyMMDD_hhmmss bin_num
Steps 1 and 2 in old will be done automatically in the python script.
If there are large baseline ripples, line window should be selected carefully.
Usually, narrow line window give better baseline fitting.
Or Edit below parameters in the python script to select base window range and seperation from line window.
    base_degree = 3
    bw_shift_factor = 0.5
    bw_width_factor = 4

For Focusing in Z-direction,
$./l5z_analysis_lu.py spect5Z_yyMMDD_hhmmss bin_num
##############

- The program will show a figure that displays spectra at 5 offsets, and of both IF1 (4-6 GHz) and IF2 (6-8 GHz). User can zoom in to find the proper line location. Select the frequency range for spectral flux integration, and input them at the program prompt.

- Then another figure appearing shows the Gaussian fits of the flux along the AZ and EL axes, where the peaks indicate the pointing errors.

- Next the program will ask two questions: first, whether update antenna's azoff & eloff with the derived errors for next iteration, and second, whether save the results in a file "$HOME/pointing/pointingLog_spect5Pt" for building the radio pointing model.

