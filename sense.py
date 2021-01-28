#!/usr/bin/python

#BUCKET_NAME="GT Thule Trailer 1"
#BUCKET_KEY="THBQ6TASXPTA"
#ACCESS_KEY="tt3u5XfTVeGWdWrtWtPnCvLNIMWg6pJO"

import os
import subprocess
import time
import math
import datetime
#from ISStreamer.Streamer import Streamer
from sense_hat import SenseHat

#streamer = Streamer(bucket_name=BUCKET_NAME,bucket_key=BUCKET_KEY,access_key=ACCESS_KEY)

#streamer.log("My messages","Stream starting")

sense = SenseHat()
#sense.show_message("GT",text_colour=[255,023,40])
sense.set_imu_config(True,True,True)

i=0
while True:

    f=open("dataSenseHat.txt","a")
    epoch = time.time()
    timestamp=datetime.datetime.fromtimestamp(epoch).strftime('%Y-%m-%d %H:%M:%S')

    temp=sense.get_temperature()
    temp=round(temp,2)

    response = subprocess.check_output("vcgencmd measure_temp", shell=True)
    (tempstring,tempvalue)=response.split("=")
    (cputemp,remainingstring)=tempvalue.split("'")
       
    humid=sense.get_humidity()
    humid=round(humid,2)
    press=sense.get_pressure()
    press=round(press,2)

    orientation=sense.get_orientation_degrees()
    pitch=round(orientation['pitch'],2)
    yaw=round(orientation['yaw'],2)
    roll=round(orientation['roll'],2)

    rawCompass=sense.get_compass_raw()
    Bx=round(rawCompass['x'],2)
    By=round(rawCompass['y'],2)
    Bz=round(rawCompass['z'],2)
    
    rawGyro=sense.get_gyroscope_raw()
    Gx=round(math.degrees(rawGyro['x']),2)
    Gy=round(math.degrees(rawGyro['y']),2)
    Gz=round(math.degrees(rawGyro['z']),2)

    rawAccel=sense.get_accelerometer_raw()
    Ax=round((980.*rawAccel['x']),2)
    Ay=round((980.*rawAccel['y']),2)
    Az=round((980.*rawAccel['z']),2)
    
    print("Time: %s %s" % (epoch,timestamp))
    print("Temp: %s C Humid: %s %% Pres: %s mbar" %(round(temp,1),humid,press))
    print("CPU temp: %s C" % cputemp)
    print("p: %s, r: %s, y: %s" % (pitch,roll,yaw))
    print("Bx: %s, By: %s, Bz: %s" % (Bx,By,Bz))
    print("Gx: %s, Gy: %s, Gz: %s" % (Gx,Gy,Gz))
    print("Ax: %s, Ay: %s, Az: %s" % (Ax,Ay,Az))
    buffer = "%s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s %s\n" % \
              (epoch,timestamp,round(temp,1),humid,press,cputemp\
              ,pitch,roll,yaw,Bx,By,Bz,Gx,Gy,Gz,Ax,Ay,Az)
    f.write(buffer)
    f.close()
#    streamer.log("epoch",epoch)
#    streamer.log("timestamp",timestamp)
#    streamer.log("Temperature",temp)
#    streamer.log("Pressure",press)
#    streamer.log("Humidity",humid)
#    streamer.log("Pitch",pitch)
#    streamer.log("Roll",roll)
#    streamer.log("Yaw",yaw)
#    streamer.log("MagneticFieldX",Bx)
#    streamer.log("MagneticFieldY",By)
#    streamer.log("MagneticFieldZ",Bz)
#    streamer.log("GyroX",Gx)
#    streamer.log("GyroY",Gy)
#    streamer.log("GyroZ",Gz)
#    streamer.log("AccelerationX",Ax)
#    streamer.log("AccelerationY",Ay)
#    streamer.log("AccelerationZ",Az)
#    streamer.log("Pi CPU temperature",cputemp) 
    time.sleep(30)
    i=i+1
    print i
#streamer.log("My messages","Stream closing")
#streamer.flush()
#streamer.close()
