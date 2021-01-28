#!/usr/bin/env python3

# analogous to fit4 for radio pointing model updates
# fits azoff = azdc*cos(el) + azcoll
#      eloff = eldc + elsag*cos(el)
# by least-squares, using scipy optimize curve_fit package

import matplotlib.pylab as plt
import numpy as np
import math as m
import scipy.optimize as opt
import sys
import csv


if len(sys.argv) < 4 or len(sys.argv) >4:
    print("Usage: fitTilt.py filename plottitle y")
    print("or: tiltFit.py filename plottitle n")
    print("y/n to remove or not remove outliers")
    sys.exit(0)

filename = sys.argv[1]
plottitle = sys.argv[2]
remove = sys.argv[3]

outlie = 1.0

def removeOutliers(x, outlierConstant):
    a = np.array(x)
    upper_quartile = np.percentile(a, 75)
    lower_quartile = np.percentile(a, 25)
    IQR = (upper_quartile - lower_quartile) * outlierConstant
    quartileSet = (lower_quartile - IQR, upper_quartile + IQR)
    resultList = []
    indexList = []
    i=0
    for y in a.tolist():
        if y >= quartileSet[0] and y <= quartileSet[1]:
            resultList.append(y)
            indexList.append(i)
        i=i+1
    return indexList

az, tiltx,tilty = np.loadtxt(filename,unpack=True,delimiter=',')
#az,tiltx,tilty,tiltxerr,tiltyerr = np.loadtxt(filename,unpack=True)
tiltxerr = [1,1,1,1,1,1,1,1,1,1,1,1,1]
tiltyerr = [1,1,1,1,1,1,1,1,1,1,1,1,1]

if (remove == 'y'):
    print("removing outliers....\n")
    indices = removeOutliers(tiltx,outlie)

    deletePoints=[]
    for i in range(len(tiltx)):
        if (i not in indices):
            deletePoints.append(i)

    az = np.delete(az,deletePoints)
    tiltx=np.delete(tiltx,deletePoints)
    tilty=np.delete(tilty,deletePoints)
    tiltxerr=np.delete(tiltxerr,deletePoints)
    tiltyerr=np.delete(tiltyerr,deletePoints)

    indices = removeOutliers(tilty,outlie)

    deletePoints=[]
    for i in range(len(tilty)):
        if (i not in indices):
            deletePoints.append(i)
    
    az = np.delete(az,deletePoints)
    tiltx=np.delete(tiltx,deletePoints)
    tilty=np.delete(tilty,deletePoints)
    tiltxerr=np.delete(tiltxerr,deletePoints)
    tiltyerr=np.delete(tiltyerr,deletePoints)

guessedAmpx=(np.amax(tiltx)-np.amin(tiltx))/2.0
guessedAmpy=(np.amax(tilty)-np.amin(tilty))/2.0
tiltxfitguess=np.array([np.mean(tiltx),guessedAmpx,guessedAmpx,0.0,0.0])
tiltyfitguess=np.array([np.mean(tilty),guessedAmpy,guessedAmpy,0.0,0.0])

def tiltfit(az,dc,a1,a2,a3,a4):
    return dc+a1*np.sin(np.radians(az))+a2*np.cos(np.radians(az))\
               +a3*np.sin(2.0*np.radians(az))+a4*np.cos(2.0*np.radians(az))

xdata = np.array(az)
ydata = np.array(tiltx)
(result,covar)=opt.curve_fit(tiltfit,xdata,ydata,tiltxfitguess,tiltxerr,absolute_sigma=True)
(dcfit,a1fit,a2fit,a3fit,a4fit)=result
s_sq = sum((tiltfit(az,dcfit,a1fit,a2fit,a3fit,a4fit)-tiltx)**2.)/(len(tiltx)-2.)
perr=np.sqrt(np.diag(covar))
(dcfiterr,a1fiterr,a2fiterr,a3fiterr,a4fiterr)=np.sqrt(np.diag(covar))

print ("tilt-x fit results (arcsec):")
print ("--------------------")
print ("dc = %.2f +/- %.2f" % (dcfit,dcfiterr))
print ("a1 = %.2f +/- %.2f" % (a1fit,a1fiterr))
print ("a2 = %.2f +/- %.2f" % (a2fit,a2fiterr))
print ("a3 = %.2f +/- %.2f" % (a3fit,a3fiterr))
print ("a4 = %.2f +/- %.2f" % (a4fit,a4fiterr))
print ("tiltfit rms=%.2f" % np.sqrt(s_sq))
print ("\n")

tiltfitString = "%.2f + %.2f * sin(az) + %.2f * cos(az) + %.2f * sin(2 az) + %.2f * cos(2 az)" %  (dcfit,a1fit,a2fit,a3fit,a4fit)

azt = np.linspace(0,360,100)

fig = plt.figure()
fig.suptitle(plottitle)

ax1 = fig.add_subplot(212)
ax1.set_xlabel('Az (deg)',fontsize=14)
ax1.set_ylabel('Tilt-X (")',fontsize=14)
ax1.text(10,np.amax(tiltx)-3,tiltfitString,fontsize=11,color='grey')
ax1.set_xlim(0,360)
ax1.set_ylim(np.amin(tiltx)-5,np.amax(tiltx)+5)
ax1.errorbar(az,tiltx,fmt='ro',yerr=tiltxerr)
ax1.plot(azt,tiltfit(azt,dcfit,a1fit,a2fit,a3fit,a4fit),'r',
         azt,tiltfit(azt,dcfit+dcfiterr,a1fit+a1fiterr,a2fit+a2fiterr,a3fit+a3fiterr,a4fit+a4fiterr),'b:',
         azt,tiltfit(azt,dcfit-dcfiterr,a1fit-a1fiterr,a2fit-a2fiterr,a3fit-a3fiterr,a4fit-a4fiterr),'g:')

tiltxmag=np.sqrt(a1fit*a1fit+a2fit*a2fit)
tiltxdir=np.degrees(np.arctan2(a1fit,a2fit))
#print(tiltxmag,tiltxdir)


xdata = np.array(az)
ydata = np.array(tilty)
(result,covar)=opt.curve_fit(tiltfit,xdata,ydata,tiltyfitguess,tiltyerr,absolute_sigma=True)
(dcfit,a1fit,a2fit,a3fit,a4fit)=result
s_sq = sum((tiltfit(az,dcfit,a1fit,a2fit,a3fit,a4fit)-tilty)**2.)/(len(tilty)-2.)
perr=np.sqrt(np.diag(covar))
(dcfiterr,a1fiterr,a2fiterr,a3fiterr,a4fiterr)=np.sqrt(np.diag(covar))

print ("tilt-y fit results (arcsec):")
print ("--------------------")
print ("dc = %.2f +/- %.2f" % (dcfit,dcfiterr))
print ("a1 = %.2f +/- %.2f" % (a1fit,a1fiterr))
print ("a2 = %.2f +/- %.2f" % (a2fit,a2fiterr))
print ("a3 = %.2f +/- %.2f" % (a3fit,a3fiterr))
print ("a4 = %.2f +/- %.2f" % (a4fit,a4fiterr))
print ("tiltfit rms=%.2f" % np.sqrt(s_sq))
print ("\n")


tiltfitString = "%.2f + %.2f * sin(az) + %.2f * cos(az) + %.2f * sin(2 az) + %.2f * cos(2 az)" %  (dcfit,a1fit,a2fit,a3fit,a4fit)

ax2 = fig.add_subplot(211)
#ax2.set_xlabel('Az (deg)',fontsize=14)
ax2.set_ylabel('Tilt-Y (")',fontsize=14)
ax2.text(10,np.amax(tilty)-3,tiltfitString,fontsize=11,color='grey')
ax2.set_xlim(0,360)
ax2.set_ylim(np.amin(tilty)-5,np.amax(tilty)+5)
ax2.errorbar(az,tilty,fmt='ro',yerr=tiltyerr)
ax2.plot(azt,tiltfit(azt,dcfit,a1fit,a2fit,a3fit,a4fit),'r',
         azt,tiltfit(azt,dcfit+dcfiterr,a1fit+a1fiterr,a2fit+a2fiterr,a3fit+a3fiterr,a4fit+a4fiterr),'b:',
         azt,tiltfit(azt,dcfit-dcfiterr,a1fit-a1fiterr,a2fit-a2fiterr,a3fit-a3fiterr,a4fit-a4fiterr),'g:')

tiltymag=np.sqrt(a1fit*a1fit+a2fit*a2fit)
tiltydir=np.degrees(np.arctan2(a1fit,a2fit))
tiltydir=tiltydir-90.
if (tiltydir<0.0):
    tiltydir=360.+tiltydir

#print(tiltymag,tiltydir)

print("Tilt magnitude=%.1f, towards %.1f deg azimuth.\n"
                %((tiltxmag+tiltymag)/2.0,(tiltxdir+tiltydir)/2.0))

plt.show()
