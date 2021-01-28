# coding: utf-8

import os
import time
from datetime import timedelta
import datetime
import numpy as np
from scipy.optimize import curve_fit
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import fnmatch
import sys
from scipy import interpolate
import pandas as pd

if len(sys.argv) < 3 or len(sys.argv) > 3:
	print("Usage: python 1ppsdelayrate_interpol.py starttime_UT_as yyyy/mm/dd hh:mm:ss")
	sys.exit(0)

startday = sys.argv[1]
starttime = sys.argv[2] 
#devide into year,month, day, hour, conversion to doy
start=[startday,starttime]
obs_start_daytime=' '.join(start)

#generate the array of time-stamp-odered 1pps files
xs = [] 
def sort_mtime(rootdir):
	for root, dir, files in os.walk(rootdir):
		for file in files:
			if fnmatch.fnmatch(file, '*.txt'):
				path = os.path.join(root, file)
				xs.append((os.path.getmtime(path), path))

	for mtime, path in sorted(xs):
		name = os.path.basename(path)
		t = datetime.datetime.fromtimestamp(mtime) #TST order
		
def main():
	sort_mtime('.')
	
if __name__ == '__main__':
	main()
	
#define function for getting the index of the nearest value in the array
def getNearestValue(list, num): #list:data array, num: target value, return: index of the nearest value
	idx = np.abs(np.array(list)-num).argmin()
	return idx
	

dt=datetime.datetime.strptime(obs_start_daytime, '%Y/%m/%d %H:%M:%S')

#perform cubic interpolation and derive time difference between gps and roachs for all files
stamp=[]
gr1=[]
gr2=[]
for mtime, path in sorted(xs):
	t = datetime.datetime.fromtimestamp(mtime)
	ts=t-(dt + timedelta(hours=8)) #from ut to 1pps time stamp, elapsed time from start
	tm=ts.total_seconds()/60.0 
	
	data=np.loadtxt(path,skiprows=3)
	us,gps,roach1,roach2,gps2=data.T
	
	gpsy=(max(gps)+min(gps))/2.0
	r1y=(max(roach1)+min(roach1))/2.0
	r2y=(max(roach2)+min(roach2))/2.0
	
	l=0
	while l < gps.shape[0]-1:
		if gps[l] > gpsy:
			break
		l += 1	
	gpsmx=(gpsy-gps[l-1])*(us[l]-us[l-1])/(gps[l]-gps[l-1])+us[l-1]
	
	m=0
	while m < roach1.shape[0]-1:
		if roach1[m] > r1y:
			break
		m += 1		
	r1mx=(r1y-roach1[m-1])*(us[m]-us[m-1])/(roach1[m]-roach1[m-1])+us[m-1]
	
	n=0
	while n < roach2.shape[0]-1:
		if roach2[n] > r2y:
			break
		n += 1
	r2mx=(r2y-roach2[n-1])*(us[n]-us[n-1])/(roach2[n]-roach2[n-1])+us[n-1]
	
	gpr1=(r1mx-gpsmx)*1000
	gpr2=(r2mx-gpsmx)*1000
	if(gpr1>-25000 and gpr1<25000 and gpr2>-25000 and gpr2<25000): #delay 25 us threshold, !!you may need to change here!!
		gr1.append(gpr1)
		gr2.append(gpr2)
		stamp.append(tm)
	else:
		print 'file %s has outliers' %path
		print '1pps waveform was saved. Check GPS server status.'
		print 'Delay fitting will be performed without this data\n'
		plt.plot(us,gps,label='GPS')
		plt.plot(us,roach1,label='R2DBE12') #roach1
		plt.plot(us,roach2,label='R2DBE13') #roach2
		plt.title(path)
		plt.xlabel('usec',size=16)
		plt.ylabel('amp(V)',size=16)
		plt.legend()
		print(path)
		pngname=path + '.png'
		plt.savefig(pngname,format='png',dpi=300)
		#plt.show()


plt.plot(stamp,gr1,'o',label='R2DBE12-GPS')
plt.plot(stamp,gr2,'*',label='R2DBE13-GPS')

f1,cv1=np.polyfit(stamp, gr1, 1, cov=True)
fit1 = np.poly1d(f1) #f1[0]*x+f1[1]
plt.plot(stamp, fit1(stamp), label='fit1')
rate1=f1[0]/1.0e9/60.0 #sec/sec
rateer1=np.sqrt(cv1[0][0])/1.0e9/60.0
if(np.sqrt(cv1[1][1])>1):
	print 'Delay error of R2DBE1-GPS is too large. Please check the outliers in the fitting.'
	print 'Fitting Results:'
	print 'fit1(nsec) = %.3f (+/- %.3f) t(min) + %.1f (+/- %.1f)' % (f1[0],np.sqrt(cv1[0][0]),f1[1],np.sqrt(cv1[1][1]))
	print 'Rate1 = %.3e +/- %.3e (sec/sec)' % (rate1,rateer1)
	print 'Delay1_start = %.1f +/- %.1f (nsec)' % (f1[1],np.sqrt(cv1[1][1]))
else:
	print 'Fitting Results:'
	print 'fit1(nsec) = %.3f (+/- %.3f) t(min) + %.1f (+/- %.1f)' % (f1[0],np.sqrt(cv1[0][0]),f1[1],np.sqrt(cv1[1][1]))
	print 'Rate1 = %.3e +/- %.3e (sec/sec)' % (rate1,rateer1)
	print 'Delay1_start = %.1f +/- %.1f (nsec)' % (f1[1],np.sqrt(cv1[1][1]))


f2,cv2=np.polyfit(stamp, gr2, 1, cov=True)
fit2 = np.poly1d(f2) #f2[0]*x+f2[1]
plt.plot(stamp, fit2(stamp), label='fit2')
rate2=f2[0]/1.0e9/60.0
rateer2=np.sqrt(cv2[0][0])/1.0e9/60.0
if(np.sqrt(cv2[1][1])>1):
	print 'Delay error of R2DBE2-GPS is too large. Please check the outliers in the fitting.'
	print 'fit2(nsec) = %.3f (+/- %.3f) t + %.1f (+/- %.1f)' % (f2[0],np.sqrt(cv2[0][0]),f2[1],np.sqrt(cv2[1][1]))
	print 'Rate2 = %.3e +/- %.3e (sec/sec)' % (rate2,rateer2)
	print 'Delay2_start = %.1f +/- %.1f (nsec)\n' % (f2[1],np.sqrt(cv2[1][1]))
else:
	print 'fit2 = %.3f (+/- %.3f) t + %.1f (+/- %.1f)' % (f2[0],np.sqrt(cv2[0][0]),f2[1],np.sqrt(cv2[1][1]))
	print 'Rate2 = %.3e +/- %.3e (sec/sec)' % (rate2,rateer2)
	print 'Delay2_start = %.1f +/- %.1f (nsec)\n' % (f2[1],np.sqrt(cv2[1][1]))


ydhm=dt.strftime('%Yy%jd%Hh%Mm')
f1u=f1[1]/1000.0
f2u=f2[1]/1000.0
print 'Please send all the following lines to people who are in charge of correlation:\n'
print 'R2DBE12 (Mark6-4065)'
print '$CLOCK;\n  def Gl; clock_early = %s : %.3f usec: %s : %.2e; enddef;\n' %(ydhm,f1u,ydhm,rate1)
print 'R2DBE13 (Mark6-4066)'
print '$CLOCK;\n  def Gl; clock_early = %s : %.3f usec: %s : %.2e; enddef;' %(ydhm,f2u,ydhm,rate2)
print 'Please note that the unit of rate is sec/sec.'


plt.xlabel('Time(minutes)',size=16)
plt.ylabel('Delay(nsec)',size=16)
plt.legend()
T0='Time0= '+ obs_start_daytime +' (UT)'
plt.title(T0)
test=startday.split("/")
pngfin=test[0] + test[1] + test[2] +".png"
plt.savefig(pngfin,format='png',dpi=300)
#plt.show()
