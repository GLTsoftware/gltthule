###
### How to take continuum data with antenna scan
###

In window 1, ssh to optical/continuum computer as

> ssh continuum@occ

Password is the usual one.  Then move to /home/continuum/bin/,
and run the following program:

> python3 cont_rpc_server.py

This is the continuum detector server.

Then in window 2, open obscon window, go to /home/obscon/pointing/,
and setup the antenna scan speed

> offsetUnit -s XX

Here, "XX" is the antenna scanning speed with the unit of
arcsec/second (but due to not well tuned the gltTrack.c,
now the actual speed is about 60% of what it defined).

Then move the antenna to the starting position of the scan as

> azoff -s XXXX

for Azimuth scan, or

> eloff -s YYYY

for Elevation scan.  For both XXXX or YYYY, put value in the
unit of arcsec.

Then start scanning with

> azscan

for Azimuth scan, or

> elscan

for Elevation scan.  At the same timing, in window 3, open
obscon window, go to /home/obscon/pointing/, run

> python3 recordContinuum.py ZZZ

to record the continuum data.  ZZZ is in second, to tell the
continuum server how long you want to take data.  This must
be defined by the scan speed and the range you want to scan.

To stop the scan,

> stopScan


The data file will be produced with the name
"contData_yymmdd_hhmmss".  The data file format is

Date/Time,AZ,AZoffset,AZerror,EL,ELoffset,ELerror,ContinuumCh0,ContinuumCh1

For the old data, please move to /home/obscon/pointing/cont_data/.

For data analysis,
> python3 rscan_pfit<3,4>.py contData_*****
