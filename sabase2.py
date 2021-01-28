#!/usr/bin/env python3

import os
import array
import time
import socket
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
#matplotlib.use('TkAgg')


global ip, addr 
#ip = "localhost"
ip = "192.168.1.99"
port = 5025

#========================================================================
def init_device():
    global socktc

    # Open TCP connect to port 5025 
    socktc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)
    socktc.connect((ip, port))

    # Query device type
    cmd = "*IDN?\n"
    x = querySA(cmd)
    print(x)

    # Preset
    cmd = "syst:pres\n"
    socktc.send(cmd.encode())
    time.sleep(1.0)
    CheckError()

def set_device():
    global socktc

    # Open TCP connect to port 5025 
    socktc = socket.socket(socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP)

    socktc.connect((ip, port))
def CheckError():
    socktc.send("SYST:ERR?\n".encode())

    s = None

    try:
        s = socktc.recv(8192)
    except socket.timeout:
        s = ""

    if s[:1] is not "0":
       print(s)

def querySA(cmd):
    socktc.send(cmd.encode())
    try:
       ret = socktc.recv(4096)
    except socket.timeout:
       ret = ""
    return ret


def sendSA(cmd):
    cmd = cmd + "\n"
    socktc.send(cmd.encode())

def setCF(val):
    cmd = "freq:cent " + str(val) + " MHZ\n"
    sendSA(cmd)
    
def getCF():
    cmd = "freq:cent?\n"
    return float(querySA(cmd).strip())
    
def setSP(val):
    cmd = "freq:span " + str(val) + " MHZ\n"
    sendSA(cmd)
    
def getSP():
    cmd = "freq:span?\n"
    return float(querySA(cmd).strip())

def setRBW(val):
    cmd = "band:res " + str(val) + " KHZ\n"
    sendSA(cmd)
    
def getRBW():
    cmd = "band:res?\n"
    return float(querySA(cmd).strip())
    
def setVBW(val):
    cmd = "band:vid " + str(val) + " KHZ\n"
    sendSA(cmd)
    
def getVBW():
    cmd = "band:vid?\n"
    return float(querySA(cmd).strip())

def setAVE(count=5):
    cmd = "AVER:COUNT " + str(count) + "\n"
    sendSA(cmd)

def gettraceSA():
    rlst=float(querySA("swe:mtim?\n").decode().strip("\n"))
    socktc.send("TRAC1:data?\n".encode())
    time.sleep(rlst+1.0)
    try:
       ret = socktc.recv(16384)
    except socket.timeout:
       ret = ""
    x=np.array(ret.decode().strip("\n").split(",")).astype(np.float)
    fc=getCF()/1.0e6
    fs=getSP()/1.0e6
    f=np.arange(fc-fs/2.0,fc+fs/2.0,fs/401)
    return f, x

def plottraceSA(f, x, plttitle=""):
    #plt.xlim(106.25, 111.75)
    if plttitle is "":
        plttitle = "Spectrum at "+time.strftime("%Y%m%d_%H%M%S")
    plt.ylim(-100.0, 0.0)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (dBm)")
    plt.title(plttitle)
    plt.grid()
    plt.plot(f,x)
    plt.savefig("spec.png")
    plt.show()
    plt.close()
