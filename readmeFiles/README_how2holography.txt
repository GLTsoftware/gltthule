###
### How to take Holography map.
###   2018/09/20  Satoki Matsushita
###   2020/02/20  Updated by Satoki Matsushita & Nimesh Patel
###

0. You need two windows, one for obscon (192.168.1.11), another
   for optel-cont (occ).
   1. Login obscon
      > cd holo
   2. Login occ
      > ssh holography@occ
      > pw: juniperotckr
      > cd rrao/holo
      > conda activate
          <=  To setup the python environment

1. Move the antenna to the holography beacon position.
     @ obscon
     > azel -a 230.214 -e 2.6817

2. Setup pointing model
     @ gltacc
     > cd ~/glttrack
     > cp pointingModel-Holography pointingModel
     > sudo systemctl restart dsm.service
     > sudo systemctl restart glttrack.service

3. Setup focus position
     @ obscon
     > cd ~/pointing/
     > ./readyHolo

4. For AZ scan map (1-D scan)
   1. Need to run the following 2 script almost simultaneously.
      @ obscon
      > cpy3 az_scan.py 0

      @ occ
      > ./vvmHoloAzel.py -n 200000
        <== Currently no averaging due to the phase biphurcation.
            See gltblog.asiaa.sinica.edu.tw/?p=2802
      ### python3 vvmHoloAzel.py -n 200000  <- This "python3" command do not recognize "scipy"
   2. Copy the data file at occ to obscon
      @ occ
      > scp data/holoADC-AzEl-YYYYMMDD_HHMMSS.txt obscon@192.168.1.11:~/holo/data/
   3. Plot the data
      @ obscon
      > gnuplot
      > plot 'holoADC-AzEl-YYYYMMDD_HHMMSS.txt' u 2:4 w d
        <== Plot AZ vs Amp
      > plot 'holoADC-AzEl-YYYYMMDD_HHMMSS.txt' u 1:5 w d
        <== Plot Time vs Phase

5. Holography mapping
   1. Edit the "holo_scan.py" to decide how big the map area to be.
      In case of 128x128 mapping, take out "#" in front of
        map_range =   0.729   # +- deg  <= 128 x 128 pix map <= 14.0 cm res.
      and put "#" in front of other "map_range" line.
   2. Each map size has a different command for occ, so choose the correct one
      (proper command is below each "map_range" line)
   3. Need to run the following 2 script almost simultaneously.
      @ obscon
      > cpy3 holo_scan.py

      @ occ
      > ./vvmHoloAzel.py -n 10000000 -s 3
        <== This command is for 128x128 mapping.
   4. ADC offset calibration
      @ occ
      > ./calibpost.py holoADC-AzEl-YYYYMMDD_HHMMSS.txt
   5. Copy the data file at occ to obscon
      @ occ
      > scp data/holoADC-AzEl-YYYYMMDD_HHMMSS-calib.txt obscon@192.168.1.11:~/holo/data/


