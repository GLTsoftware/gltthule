##
## 5-points spectral pointing, data taking & errors derivation
##

=== Preparation for Spectrometer PC ===

- Login the spectrometer PC as root@192.168.1.25, and cd to /data2/glt.

- Check and edit acc_len in all glt_32k_*.conf:
      acc_len = 2000    # original value, 32msec integration per chunk
      acc_len = 20000   # 320msec integration per chunk
  
  or use the script to set the factor:
$ python2.7 glt_set_acclen.py glt_32k_*.conf -I 3   # 3 x 32msec

- If necessary (ex. acc_len change, not using the spectrometer for sometime, or after power outage), manually execute full ROACH initialization:
$ python2.7 glt_init_LHC.py glt_32k_LHC.conf -a -v
$ python2.7 glt_init_RHC.py glt_32k_RHC.conf -a -v 
$ python2.7 /data/glt/adc_cal/ioDelayIQSetup.py 192.168.50.15 -s
$ python2.7 /data/glt/adc_cal/ioDelayIQSetup.py 192.168.50.16 -s

- check if there is a previous server instance running in a screen session:
$ ps aux | grep -i ctrl_rpc_server
$ screen -ls
$ screen -d -r [PID | -S NAME]	# enter the screen session. Ctrl+A then D to detach.

- if you can't find in screen, then kill that server process and re-run in a screen session.
$ screen -S server	# create a new session named 'server'
(screen)$ source /data/miniconda3/bin/activate spectctl
(screen) (spectctl) $ python3 /home/ACC/ctrl_rpc_server.py
# Ctrl+A then D to detach the screen


=== Preparation for Obscon ===

- 2018 Dec. Now spectral data (data2) is mounted under /Spect_Data via NFS. The old method below is obsolete and only optional.

>* mount Spectrometer PC filesystem via GVFS/SFTP
>* On Ubuntu Desktop, launch the "Files" app and use "Connect to Server" at the left panel. Select the connection history item to 192.168.1.25. A symbolic link $HOME/pointing/spectrometer_data2_glt now shall point to the remote data dir SpectPC:/data2/glt.

- Make the antenna start tracking the desired line source. If there are presets for azoff and/or eloff, also enter now.


=== Obtain Data ===

- At Obscon, cd $HOME/pointing/. Display the usage of data acquisition program:
$ cpy3 l5pt_client.py -h

- Run the script with arguments and options:
$ cpy3 l5pt_client.py [...]

- Once done, a meta file as "spect5Pt_yyMMDD_hhmmss" will be generated.


=== Analyze the Data and Derive the Pointing Errors ===

- Display the usage of analysis program:
$ cpy3 l5pt_analysis.py -h

- Run the script with arguments and options:
$ cpy3 l5pt_analysis.py [...]

# Note the program will no longer copy the h5 files to the current working directory.

- The program will show a figure that displays spectra at 5 offsets, and of both IF1 (4-6 GHz) and IF2 (6-8 GHz). User can zoom in to find the proper line location. Select the frequency range for spectral flux integration, and input them at the program prompt.

- Then another figure appearing shows the Gaussian fits of the flux along the AZ and EL axes, where the peaks indicate the pointing errors.

- Next the program will ask two questions: first, whether update antenna's azoff & eloff with the derived errors for next iteration, and second, whether save the results in a file "$HOME/pointing/pointingLog_spect5Pt" for building the radio pointing model.


=== Edition History ===
* 2017.03.28 - The first version.
* 2018.08.21 - Revised for the latest version of l5pt_client.py & l5pt_analysis.py. Include the modification made by Byun and the support of repeat mode.
* 2018.12.26 - Conda environment, NFS-ounted SpectPC spectral data on Obscon so revised accordingly.
