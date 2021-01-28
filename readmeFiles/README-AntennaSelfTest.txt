###
### Antenna Self Test (from obscon)
###
### !!! Caution !!!
###   Since antenna will move around, make sure no obstacles around
###   the antenna, and the sky is clear.
###
### 2018/12/04
###   written by Satoki Matsushita (ASIAA)
###   based on information from Nimesh (SAO) and Dirk (Vertex).
###

0. Set ACU as "Remote" mode.
1. Issue "unstow"
2. Issue "stop"
3. Issue "setSelfTest"
   AZ/EL modes in the glttrack will show "Self Test".
4. To monitor the progress:
     "ssh gltacc"
   then
     "cd acuCommands"
   then
     "./acuSelftestResults"
   You can command this program anytime. It will not affect any
   telescope behavior.

5. After the self test finished, download the log from ACU:
     "ftp 192.168.1.103"
   then
     "cd ACULOG"
   then
     "get Selftest.log"
6. In case, there is an error showing
     "Too many open files"
   then reboot the ACU.
   If you do not know how to reboot, ask someone who knows well.

