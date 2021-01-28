########################################################
README-5p-el.pl
version: 2018.Feb.21th

Script was originally made by Hiroaki,
Keiichi, Nimesh revised later on.


README was written by Kuan-Yu and Keiichi revised
########################################################


5p-el.pl will operate the antenna with 5 points scan in the elevation direction, 
and then output 10 set of record spectra data.
In order to take a data, please track the target source at obscon,
and issue the 5p-el.pl

obscon@gltobscon:~/pointing> observe -s satoki
obscon@gltobscon:~/pointing> ./5p-el.pl

The script is at

/home/obscon/pointing


Before moving to the 5 points to take spectrum, telescope move to the off point



off point         5 pts

                    1
                    3
0, 2, 4, 6, 8       5
                    7
                    9

number describe order of the scan.

The 1st point is the center point with EL offset + 2x.
The 2nd point is the center point with El offset +.
The 3rd point is the center point with Az offset 0.
The 4th point is the center point with El offset -.
The 5th point is the center point with El offset - 2x.

offset and offpoint are described in 5p-el.pl as 

$offset=40;
$offpoint=180;

unit is arcsec.  Central positions for the az and el are also described as

$centeraz=$origAzoff;
$centerel=$origEloff;

The spectra are recorded by the script takeSpectrum.sh. 
All files will be saved in 

root@localhost/data/glt

with hd5 formats with timestamp. 

The command is sent to spectrometer pc and take spectrum data.

In order to change the itegration time of the spectrum, 
number after the "./runsetupglt2.sh" in the takeSpectrum

./runsetupglt2.sh 300

Unit is [sec].  Further information, please take a look on 
README-takeSpectrum at obscon@gltobscon:~/pointing$


