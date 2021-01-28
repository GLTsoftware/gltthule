http://gltblog.asiaa.sinica.edu.tw/?p=3759

Posted on October 12, 2019 by Satoki Matsushita
New Tsys Measurement Scripts for future VLBI runs

Because of the VLBI measurements requirement, I made a script to measure Tsys every second and record into a file. There is already a program exists (probably made by Nimesh while ago), but since a lot of things updated, especially various DSM variables now available from various instruments, thanks to Ranjani and Locutus, I updated the available program to match the current system and for almost full automation recording.

In a VLBI observation script, put
“cpy3 ~/stability/hotload_rec.py”
to put hotload in when the antenna is slewing to the next source. This program puts the hotload power information into DSM. I made an example VLBI observation script “~/pointing/VLBI-sched-example20191012.pl”, so please have a look at this. Here, the assumption is that the hotload value does not change while observing one source.

In parallel, when a VLBI observation is ongoing, run
“cpy3 ~/stability/tsysLoop_pm.py”
in a different window. This program calculates Tsys every second using powermeter outputs, various temperatures, and the hotload power that measured with the above script, and record the calculated Tsys data into a file “TsysData_YYMMDD_HHMMSS”. When the hotload is in, Tsys shows crazy values, but that can be flagged out later easily.

