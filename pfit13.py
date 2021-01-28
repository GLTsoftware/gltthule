#!/common/anaconda/bin/python
#!//Users/nimesh/anaconda3/bin/python

import matplotlib.pylab as plt
#import plotly.tools as tls
import numpy as np
import math as m
import scipy.optimize as opt
import sys
import time
from matplotlib.ticker import MultipleLocator,FormatStrFormatter

if len(sys.argv) < 6 or len(sys.argv) >6:
    print("Usage: pfit.py filename plottitle y")
    print("or: rfit.py filename plottitle n ")
    print("y/n to remove or not remove outliers")
    sys.exit(0)

filename = sys.argv[1]
plottitle = sys.argv[2]
r = sys.argv[3] # y/n
opticalOrRadio = sys.argv[4] # optical/radio
azencRemoveFlag = int(sys.argv[5]) # 0/1

today = time.strftime("%d%b%y")

outlie = 1.0
header=[]
opticalModel={}
radioModel={}
i=0
f = open('pointingModel','r')
for line in f:
    line = line.strip()
    if(line.startswith("#")):
        header.append(line)
        i=i+1
    else:
        columns = line.split()
        parameter = columns[0]
        optical = columns[1]
        radio = columns[2]
        opticalModel[parameter]=optical
        radioModel[parameter]=radio
f.close()

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


no,source,az,el,azoff,eloff,azofferr,elofferr,utc,timestamp =\
   np.loadtxt(filename,dtype={'names':('no','source','az','el','azoff','eloff','azofferr','elofferr','utc','timestamp'),'formats':('i4','a8','f8','f8','f8','f8','f8','f8','f8','a14')},unpack=True)

# if azencRemoveFlag is 1, then subtract the azimuth encoder eccentricity as in existing model
# for optical or radio, as requested. 

if (azencRemoveFlag==1):
    azr = np.radians(az)
    elr = np.radians(el)
    if(opticalOrRadio=="optical"):
        azoff = azoff - np.cos(elr)*(float(opticalModel["AzEncSin"])*np.sin(azr)+\
                                     float(opticalModel["AzEncCos"])*np.cos(azr)+\
                                     float(opticalModel["AzEncSin2"])*np.sin(2.0*azr)+\
                                     float(opticalModel["AzEncCos2"])*np.cos(2.0*azr)+\
                                     float(opticalModel["AzEncSin3"])*np.sin(3.0*azr)+\
                                     float(opticalModel["AzEncCos3"])*np.cos(3.0*azr))
    if(opticalOrRadio=="radio"):
        azoff = azoff - np.cos(elr)*(float(radioModel["AzEncSin"])*np.sin(azr)+\
                                     float(radioModel["AzEncCos"])*np.cos(azr)+\
                                     float(radioModel["AzEncSin2"])*np.sin(2.0*azr)+\
                                     float(radioModel["AzEncCos2"])*np.cos(2.0*azr)+\
                                     float(radioModel["AzEncSin3"])*np.sin(3.0*azr)+\
                                     float(radioModel["AzEncCos3"])*np.cos(3.0*azr))
 

if (r == 'y'):
    print("removing outliers....\n")
    indices = removeOutliers(azoff,outlie)

    deletePoints=[]
    for i in range(len(azoff)):
        if (i not in indices):
            deletePoints.append(i)

    az = np.delete(az,deletePoints)
    el = np.delete(el,deletePoints)
    azoff=np.delete(azoff,deletePoints)
    eloff=np.delete(eloff,deletePoints)
    azofferr=np.delete(azofferr,deletePoints)
    elofferr=np.delete(elofferr,deletePoints)

    indices = removeOutliers(eloff,outlie)

    deletePoints=[]
    for i in range(len(eloff)):
        if (i not in indices):
            deletePoints.append(i)
    
    az = np.delete(az,deletePoints)
    el = np.delete(el,deletePoints)
    azoff=np.delete(azoff,deletePoints)
    eloff=np.delete(eloff,deletePoints)
    azofferr=np.delete(azofferr,deletePoints)
    elofferr=np.delete(elofferr,deletePoints)


azfitguess=np.array([1.0,np.mean(azoff),0.0,0.0,0.0,0.0,0.0])
elfitguess=np.array([np.mean(eloff),1.0,0.0,0.0,0.0,0.0])

# azfit = the full az and el dependence of pointing model for azoff(az,el)
# we are ignoring any az encoder eccentricity terms for now
def azfit(pos,azdc,azcoll,eltilt,aaztltsin,aaztltcos,aaztltsin2,aaztltcos2):
    azrad = np.radians(pos[0])
    elrad = np.radians(pos[1])
    return azdc * np.cos(elrad) + azcoll + eltilt*np.sin(elrad)\
                    + aaztltsin*np.sin(elrad)*np.sin(azrad)  \
                    - aaztltcos*np.sin(elrad)*np.cos(azrad)  \
                    + aaztltsin2*np.sin(elrad)*np.sin(2.0*azrad)  \
                    - aaztltcos2*np.sin(elrad)*np.cos(2.0*azrad)




# azFnAzfit = only the az dependence of azoff (due to az axis tilt)
# we are ignoring any az encoder eccentricity terms for now
def azFnAzfit(pos,aaztltsin,aaztltcos,aaztltsin2,aaztltcos2):
    azrad = np.radians(pos[0])
    elrad = np.radians(pos[1])
    return aaztltsin*np.sin(elrad)*np.sin(azrad)  \
                    - aaztltcos*np.sin(elrad)*np.cos(azrad)  \
                    + aaztltsin2*np.sin(elrad)*np.sin(2.0*azrad)  \
                    - aaztltcos2*np.sin(elrad)*np.cos(2.0*azrad)

# elFnAzfit = only the el dependence of azoff (due to az axis tilt)
def elFnAzfit(pos,azdc,azcoll,eltilt):
    azrad = np.radians(pos[0])
    elrad = np.radians(pos[1])
    return azdc * np.cos(elrad) + azcoll + eltilt*np.sin(elrad)
             

# elfit = the full az and el dependence of pointing model for el(az,el)
# we are ignoring any el encoder eccentricity terms for now
# these are hard to solve for anyway, given only 0-90 max possible el coverage.
def elfit(pos,eldc,elsag,eaztltsin,eaztltcos,eaztltsin2,eaztltcos2):
    azrad = np.radians(pos[0])
    elrad = np.radians(pos[1])
    return eldc + elsag * np.cos(elrad)+\
              eaztltsin*np.cos(azrad) + eaztltcos*np.sin(azrad) + \
              eaztltsin2*np.cos(2.0*azrad) + eaztltcos2*np.sin(2.0*azrad)

# azFnElfit = only the az dependence for eloff
def azFnElfit(pos,eaztltsin,eaztltcos,eaztltsin2,eaztltcos2):
    azrad = np.radians(pos[0])
    elrad = np.radians(pos[1])
    return eaztltsin*np.cos(azrad) + eaztltcos*np.sin(azrad) + \
              eaztltsin2*np.cos(2.0*azrad) + eaztltcos2*np.sin(2.0*azrad)

# elFnElfit = only the el dependence for eloff
def elFnElfit(pos,eldc,elsag):
    azrad = np.radians(pos[0])
    elrad = np.radians(pos[1])
    return eldc + elsag * np.cos(elrad)

xdata = (np.array(az),np.array(el))
ydata = np.array(azoff)
azoffmin = np.amin(ydata)
azoffmax = np.amax(ydata)
(result,covar)=opt.curve_fit(azfit,xdata,ydata,azfitguess,azofferr,absolute_sigma=True)
(azdcfit,azcollfit,eltiltfit,aaztltsinfit,aaztltcosfit,aaztltsin2fit,aaztltcos2fit)=result
azres = azfit((az,el),azdcfit,azcollfit,eltiltfit,aaztltsinfit,aaztltcosfit,aaztltsin2fit,aaztltcos2fit)-azoff
s_sq = sum(azres**2.)/(len(azoff)-2.)
perr=np.sqrt(np.diag(covar))
(azdcfiterr,azcollfiterr,eltiltfiterr,aaztltsinfiterr,aaztltcosfiterr,aaztltsin2fiterr,aaztltcos2fiterr)=np.sqrt(np.diag(covar))

resultsFile = open("results","w")
print ("azoff fit results (arcsec):")
print ("---------------------------")
print ("azdc       = %.2f +/- %.2f" % (azdcfit,azdcfiterr))
print ("azcoll     = %.2f +/- %.2f" % (azcollfit,azcollfiterr))
print ("eltilt     = %.2f +/- %.2f" % (eltiltfit,eltiltfiterr))
print ("aaztltsin  = %.2f +/- %.2f" % (aaztltsinfit,aaztltsinfiterr))
print ("aaztltcos  = %.2f +/- %.2f" % (aaztltcosfit,aaztltcosfiterr))
print ("aaztltsin2 = %.2f +/- %.2f" % (aaztltsin2fit,aaztltsin2fiterr))
print ("aaztltcos2 = %.2f +/- %.2f" % (aaztltcos2fit,aaztltcos2fiterr))
print ("azfit rms  = %.2f" % np.sqrt(s_sq))
print ("\n")
AzRms=np.sqrt(s_sq)

resultsFile.write ("azoff fit results (arcsec):\n")
resultsFile.write ("---------------------------\n")
resultsFile.write ("azdc       = %.2f +/- %.2f\n" % (azdcfit,azdcfiterr))
resultsFile.write ("azcoll     = %.2f +/- %.2f\n" % (azcollfit,azcollfiterr))
resultsFile.write ("eltilt     = %.2f +/- %.2f\n" % (eltiltfit,eltiltfiterr))
resultsFile.write ("aaztltsin  = %.2f +/- %.2f\n" % (aaztltsinfit,aaztltsinfiterr))
resultsFile.write ("aaztltcos  = %.2f +/- %.2f\n" % (aaztltcosfit,aaztltcosfiterr))
resultsFile.write ("aaztltsin2 = %.2f +/- %.2f\n" % (aaztltsin2fit,aaztltsin2fiterr))
resultsFile.write ("aaztltcos2 = %.2f +/- %.2f\n" % (aaztltcos2fit,aaztltcos2fiterr))
resultsFile.write ("azfit rms  = %.2f\n" % np.sqrt(s_sq))
resultsFile.write ("\n")

#azfitString = "Azoff = %.2f * cos(el) %+.2f" %  (azdcfit,azcollfit)

xdata = (np.array(az),np.array(el))
ydata = np.array(eloff)
eloffmin = np.amin(ydata)
eloffmax = np.amax(ydata)
(result,covar)=opt.curve_fit(elfit,xdata,ydata,elfitguess,elofferr,absolute_sigma=True)
(eldcfit,elsagfit,eaztltsinfit,eaztltcosfit,eaztltsin2fit,eaztltcos2fit)=result
elres = elfit((az,el),eldcfit,elsagfit,eaztltsinfit,eaztltcosfit,eaztltsin2fit,eaztltcos2fit)-eloff
s_sq = sum(elres**2.)/(len(eloff)-2.)
(eldcfiterr,elsagfiterr,eaztltsinfiterr,eaztltcosfiterr,eaztltsin2fiterr,eaztltcos2fiterr)=np.sqrt(np.diag(covar))

#elfitString = "Eloff = %.2f %+.2f * cos(el)" %  (eldcfit,elsagfit)

print ("eloff fit results (arcsec):")
print ("---------------------------")
print ("eldc       = %.2f +/- %.2f" % (eldcfit,eldcfiterr))
print ("elsag      = %.2f +/- %.2f" % (elsagfit,elsagfiterr))
print ("eaztltsin  = %.2f +/- %.2f" % (eaztltsinfit,eaztltsinfiterr))
print ("eaztltcos  = %.2f +/- %.2f" % (eaztltcosfit,eaztltcosfiterr))
print ("eaztltsin2 = %.2f +/- %.2f" % (eaztltsin2fit,eaztltsin2fiterr))
print ("eaztltcos2 = %.2f +/- %.2f" % (eaztltcos2fit,eaztltcos2fiterr))
print ("elfit rms  = %.2f" % np.sqrt(s_sq))
ElRms=np.sqrt(s_sq)

resultsFile.write ("eloff fit results (arcsec):\n")
resultsFile.write ("---------------------------\n")
resultsFile.write ("eldc       = %.2f +/- %.2f\n" % (eldcfit,eldcfiterr))
resultsFile.write ("elsag      = %.2f +/- %.2f\n" % (elsagfit,elsagfiterr))
resultsFile.write ("eaztltsin  = %.2f +/- %.2f\n" % (eaztltsinfit,eaztltsinfiterr))
resultsFile.write ("eaztltcos  = %.2f +/- %.2f\n" % (eaztltcosfit,eaztltcosfiterr))
resultsFile.write ("eaztltsin2 = %.2f +/- %.2f\n" % (eaztltsin2fit,eaztltsin2fiterr))
resultsFile.write ("eaztltcos2 = %.2f +/- %.2f\n" % (eaztltcos2fit,eaztltcos2fiterr))
resultsFile.write ("elfit rms  = %.2f" % np.sqrt(s_sq))

resultsFile.close()

newModelFile = open("pointingModel.new","w")

print("Cut-and-paste the new pointing model:")
print("\n")

print("Or copy over the file pointingModel.new to /otherInstances/acc/ant<n>/configFiles area and issue the command: newPointingModel -a <n> on hal9000.")
print("\n")

for i in range(len(header)):
    print(header[i])
    newModelFile.write(header[i])
    newModelFile.write("\n")
if(opticalOrRadio=="optical"):
    AzDC=azdcfit+float(opticalModel["AzDC"])
    AzColl=azcollfit+float(opticalModel["AzColl"])
    ElTilt=eltiltfit+float(opticalModel["ElTilt"])
    AAzTltSin=aaztltsinfit+float(opticalModel["AAzTltSin"])
    AAzTltCos=aaztltcosfit+float(opticalModel["AAzTltCos"])
    AAzTltSin2=aaztltsin2fit+float(opticalModel["AAzTltSin2"])
    AAzTltCos2=aaztltcos2fit+float(opticalModel["AAzTltCos2"])
    ElDC=eldcfit+float(opticalModel["ElDC"])
    ElSag=elsagfit+float(opticalModel["ElSag"])
    EAzTltSin=eaztltsinfit+float(opticalModel["EAzTltSin"])
    EAzTltCos=eaztltcosfit+float(opticalModel["EAzTltCos"])
    EAzTltSin2=eaztltsin2fit+float(opticalModel["EAzTltSin2"])
    EAzTltCos2=eaztltcos2fit+float(opticalModel["EAzTltCos2"])
    print("AzDC          %.1f        %.1f" % (AzDC, float(radioModel["AzDC"])))
    print("AzColl        %.1f        %.1f"% (AzColl, float(radioModel["AzColl"])))
    print("ElTilt        %.1f        %.1f"% (ElTilt, float(radioModel["ElTilt"])))
    print("AAzTltSin     %.1f        %.1f"% (AAzTltSin, float(radioModel["AAzTltSin"])))
    print("AAzTltCos     %.1f        %.1f"% (AAzTltCos, float(radioModel["AAzTltCos"])))
    print("AAzTltSin2    %.1f        %.1f"% (AAzTltSin2, float(radioModel["AAzTltSin2"])))
    print("AAzTltCos2    %.1f        %.1f"% (AAzTltCos2, float(radioModel["AAzTltCos2"])))
    print("AzEncSin      %.1f        %.1f"% (float(opticalModel["AzEncSin"]), float(radioModel["AzEncSin"])))
    print("AzEncCos      %.1f        %.1f"% (float(opticalModel["AzEncCos"]), float(radioModel["AzEncCos"])))
    print("AzEncSin2     %.1f        %.1f"% (float(opticalModel["AzEncSin2"]), float(radioModel["AzEncSin2"])))
    print("AzEncCos2     %.1f        %.1f"% (float(opticalModel["AzEncCos2"]), float(radioModel["AzEncCos2"])))
    print("AzEncSin3     %.1f        %.1f"% (float(opticalModel["AzEncSin3"]), float(radioModel["AzEncSin3"])))
    print("AzEncCos3     %.1f        %.1f"% (float(opticalModel["AzEncCos3"]), float(radioModel["AzEncCos3"])))
    print("AzRms         %.1f        %.1f"% (AzRms, float(radioModel["AzRms"])))
    print("ElDC          %.1f        %.1f"% (ElDC, float(radioModel["ElDC"])))
    print("ElSag         %.1f        %.1f"% (ElSag, float(radioModel["ElSag"])))
    print("EAzTltSin     %.1f        %.1f"% (EAzTltSin, float(radioModel["EAzTltSin"])))
    print("EAzTltCos     %.1f        %.1f"% (EAzTltCos, float(radioModel["EAzTltCos"])))
    print("EAzTltSin2    %.1f        %.1f"% (EAzTltSin2, float(radioModel["EAzTltSin2"])))
    print("EAzTltCos2    %.1f        %.1f"% (EAzTltCos2, float(radioModel["EAzTltCos2"])))
    print("ElRms         %.1f        %.1f"% (ElRms, float(radioModel["ElRms"])))
    print("TiltFlag       %d          %d"%(int(opticalModel["TiltFlag"]), int(radioModel["TiltFlag"])))
    print("Date          %s          %s"% (today, radioModel["Date"]))

    newModelFile.write("AzDC          %.1f        %.1f\n" % (AzDC, float(radioModel["AzDC"])))
    newModelFile.write("AzColl        %.1f        %.1f\n"% (AzColl, float(radioModel["AzColl"])))
    newModelFile.write("ElTilt        %.1f        %.1f\n"% (ElTilt, float(radioModel["ElTilt"])))
    newModelFile.write("AAzTltSin     %.1f        %.1f\n"% (AAzTltSin, float(radioModel["AAzTltSin"])))
    newModelFile.write("AAzTltCos     %.1f        %.1f\n"% (AAzTltCos, float(radioModel["AAzTltCos"])))
    newModelFile.write("AAzTltSin2    %.1f        %.1f\n"% (AAzTltSin2, float(radioModel["AAzTltSin2"])))
    newModelFile.write("AAzTltCos2    %.1f        %.1f\n"% (AAzTltCos2, float(radioModel["AAzTltCos2"])))
    newModelFile.write("AzEncSin      %.1f        %.1f\n"% (float(opticalModel["AzEncSin"]), float(radioModel["AzEncSin"])))
    newModelFile.write("AzEncCos      %.1f        %.1f\n"% (float(opticalModel["AzEncCos"]), float(radioModel["AzEncCos"])))
    newModelFile.write("AzEncSin2     %.1f        %.1f\n"% (float(opticalModel["AzEncSin2"]), float(radioModel["AzEncSin2"])))
    newModelFile.write("AzEncCos2     %.1f        %.1f\n"% (float(opticalModel["AzEncCos2"]), float(radioModel["AzEncCos2"])))
    newModelFile.write("AzEncSin3     %.1f        %.1f\n"% (float(opticalModel["AzEncSin3"]), float(radioModel["AzEncSin3"])))
    newModelFile.write("AzEncCos3     %.1f        %.1f\n"% (float(opticalModel["AzEncCos3"]), float(radioModel["AzEncCos3"])))
    newModelFile.write("AzRms         %.1f        %.1f\n"% (AzRms, float(radioModel["AzRms"])))
    newModelFile.write("ElDC          %.1f        %.1f\n"% (ElDC, float(radioModel["ElDC"])))
    newModelFile.write("ElSag         %.1f        %.1f\n"% (ElSag, float(radioModel["ElSag"])))
    newModelFile.write("EAzTltSin     %.1f        %.1f\n"% (EAzTltSin, float(radioModel["EAzTltSin"])))
    newModelFile.write("EAzTltCos     %.1f        %.1f\n"% (EAzTltCos, float(radioModel["EAzTltCos"])))
    newModelFile.write("EAzTltSin2    %.1f        %.1f\n"% (EAzTltSin2, float(radioModel["EAzTltSin2"])))
    newModelFile.write("EAzTltCos2    %.1f        %.1f\n"% (EAzTltCos2, float(radioModel["EAzTltCos2"])))
    newModelFile.write("ElRms         %.1f        %.1f\n"% (ElRms, float(radioModel["ElRms"])))
    newModelFile.write("TiltFlag       %d          %d\n"%(int(opticalModel["TiltFlag"]), int(radioModel["TiltFlag"])))
    newModelFile.write("Date          %s          %s\n"% (today, radioModel["Date"]))
    newModelFile.close()

if(opticalOrRadio=="radio"):
    AzDC=azdcfit+float(radioModel["AzDC"])
    AzColl=azcollfit+float(radioModel["AzColl"])
    ElTilt=eltiltfit+float(radioModel["ElTilt"])
    AAzTltSin=aaztltsinfit+float(radioModel["AAzTltSin"])
    AAzTltCos=aaztltcosfit+float(radioModel["AAzTltCos"])
    AAzTltSin2=aaztltsin2fit+float(radioModel["AAzTltSin2"])
    AAzTltCos2=aaztltcos2fit+float(radioModel["AAzTltCos2"])
    ElDC=eldcfit+float(radioModel["ElDC"])
    ElSag=elsagfit+float(radioModel["ElSag"])
    EAzTltSin=eaztltsinfit+float(radioModel["EAzTltSin"])
    EAzTltCos=eaztltcosfit+float(radioModel["EAzTltCos"])
    EAzTltSin2=eaztltsin2fit+float(radioModel["EAzTltSin2"])
    EAzTltCos2=eaztltcos2fit+float(radioModel["EAzTltCos2"])
    print("AzDC          %.1f        %.1f" % (float(opticalModel["AzDC"]),AzDC))
    print("AzColl        %.1f        %.1f"% (float(opticalModel["AzColl"]),AzColl))
    print("ElTilt        %.1f        %.1f"% (float(opticalModel["ElTilt"]),ElTilt))
    print("AAzTltSin     %.1f        %.1f"% (float(opticalModel["AAzTltSin"]),AAzTltSin))
    print("AAzTltCos     %.1f        %.1f"% (float(opticalModel["AAzTltCos"]),AAzTltCos))
    print("AAzTltSin2    %.1f        %.1f"% (float(opticalModel["AAzTltSin2"]),AAzTltSin2))
    print("AAzTltCos2    %.1f        %.1f"% (float(opticalModel["AAzTltCos2"]),AAzTltCos2))
    print("AzEncSin      %.1f        %.1f"% (float(opticalModel["AzEncSin"]), float(radioModel["AzEncSin"])))
    print("AzEncCos      %.1f        %.1f"% (float(opticalModel["AzEncCos"]), float(radioModel["AzEncCos"])))
    print("AzEncSin2     %.1f        %.1f"% (float(opticalModel["AzEncSin2"]), float(radioModel["AzEncSin2"])))
    print("AzEncCos2     %.1f        %.1f"% (float(opticalModel["AzEncCos2"]), float(radioModel["AzEncCos2"])))
    print("AzEncSin3     %.1f        %.1f"% (float(opticalModel["AzEncSin3"]), float(radioModel["AzEncSin3"])))
    print("AzEncCos3     %.1f        %.1f"% (float(opticalModel["AzEncCos3"]), float(radioModel["AzEncCos3"])))
    print("AzRms         %.1f        %.1f"% (float(opticalModel["AzRms"]),AzRms))
    print("ElDC          %.1f        %.1f"% (float(opticalModel["ElDC"]),ElDC))
    print("ElSag         %.1f        %.1f"% (float(opticalModel["ElSag"]),ElSag))
    print("EAzTltSin     %.1f        %.1f"% (float(opticalModel["EAzTltSin"]),EAzTltSin))
    print("EAzTltCos     %.1f        %.1f"% (float(opticalModel["EAzTltCos"]),EAzTltCos))
    print("EAzTltSin2    %.1f        %.1f"% (float(opticalModel["EAzTltSin2"]),EAzTltSin2))
    print("EAzTltCos2    %.1f        %.1f"% (float(opticalModel["EAzTltCos2"]),EAzTltCos2))
    print("ElRms         %.1f        %.1f"% (float(opticalModel["ElRms"]),ElRms))
    print("TiltFlag       %d          %d"%(int(opticalModel["TiltFlag"]), int(radioModel["TiltFlag"])))
    print("Date          %s          %s"% (opticalModel["Date"],today))

    newModelFile.write("AzDC          %.1f        %.1f\n" % (float(opticalModel["AzDC"]),AzDC))
    newModelFile.write("AzColl        %.1f        %.1f\n"% (float(opticalModel["AzColl"]),AzColl))
    newModelFile.write("ElTilt        %.1f        %.1f\n"% (float(opticalModel["ElTilt"]),ElTilt))
    newModelFile.write("AAzTltSin     %.1f        %.1f\n"% (float(opticalModel["AAzTltSin"]),AAzTltSin))
    newModelFile.write("AAzTltCos     %.1f        %.1f\n"% (float(opticalModel["AAzTltCos"]),AAzTltCos))
    newModelFile.write("AAzTltSin2    %.1f        %.1f\n"% (float(opticalModel["AAzTltSin2"]),AAzTltSin2))
    newModelFile.write("AAzTltCos2    %.1f        %.1f\n"% (float(opticalModel["AAzTltCos2"]),AAzTltCos2))
    newModelFile.write("AzEncSin      %.1f        %.1f\n"% (float(opticalModel["AzEncSin"]), float(radioModel["AzEncSin"])))
    newModelFile.write("AzEncCos      %.1f        %.1f\n"% (float(opticalModel["AzEncCos"]), float(radioModel["AzEncCos"])))
    newModelFile.write("AzEncSin2     %.1f        %.1f\n"% (float(opticalModel["AzEncSin2"]), float(radioModel["AzEncSin2"])))
    newModelFile.write("AzEncCos2     %.1f        %.1f\n"% (float(opticalModel["AzEncCos2"]), float(radioModel["AzEncCos2"])))
    newModelFile.write("AzEncSin3     %.1f        %.1f\n"% (float(opticalModel["AzEncSin3"]), float(radioModel["AzEncSin3"])))
    newModelFile.write("AzEncCos3     %.1f        %.1f\n"% (float(opticalModel["AzEncCos3"]), float(radioModel["AzEncCos3"])))
    newModelFile.write("AzRms         %.1f        %.1f\n"% (float(opticalModel["AzRms"]),AzRms))
    newModelFile.write("ElDC          %.1f        %.1f\n"% (float(opticalModel["ElDC"]),ElDC))
    newModelFile.write("ElSag         %.1f        %.1f\n"% (float(opticalModel["ElSag"]),ElSag))
    newModelFile.write("EAzTltSin     %.1f        %.1f\n"% (float(opticalModel["EAzTltSin"]),EAzTltSin))
    newModelFile.write("EAzTltCos     %.1f        %.1f\n"% (float(opticalModel["EAzTltCos"]),EAzTltCos))
    newModelFile.write("EAzTltSin2    %.1f        %.1f\n"% (float(opticalModel["EAzTltSin2"]),EAzTltSin2))
    newModelFile.write("EAzTltCos2    %.1f        %.1f\n"% (float(opticalModel["EAzTltCos2"]),EAzTltCos2))
    newModelFile.write("ElRms         %.1f        %.1f\n"% (float(opticalModel["ElRms"]),ElRms))
    newModelFile.write("TiltFlag       %d          %d\n"%(int(opticalModel["TiltFlag"]), int(radioModel["TiltFlag"])))
    newModelFile.write("Date          %s          %s\n"% (opticalModel["Date"],today))
    newModelFile.close()

azoffEldep= np.zeros(len(az))
eloffEldep= np.zeros(len(az))
azoffAzdep= np.zeros(len(az))
eloffAzdep= np.zeros(len(az))

pos = (np.array(az),np.array(el))
azoffEldep = np.array(azoff) - azFnAzfit(pos,aaztltsinfit,aaztltcosfit,aaztltsin2fit,aaztltcos2fit) 
eloffEldep = np.array(eloff) - azFnElfit(pos,eaztltsinfit,eaztltcosfit,eaztltsin2fit,eaztltcos2fit) 
azoffAzdep = np.array(azoff) - elFnAzfit(pos,azdcfit,azcollfit,eltiltfit) 
eloffAzdep = np.array(eloff) - elFnElfit(pos,eldcfit,elsagfit) 


#debug
#for i in range(len(az)):
#    pos = (az[i],el[i])
#    azoffEldep[i] = azoff[i] - azFnAzfit(pos,aaztltsinfit,aaztltcosfit,aaztltsin2fit,aaztltcos2fit) 
#    eloffEldep[i] = eloff[i] - azFnElfit(pos,eaztltsinfit,eaztltcosfit,eaztltsin2fit,eaztltcos2fit) 
#    azoffAzdep[i] = azoff[i] - elFnAzfit(pos,azdcfit,azcollfit,eltiltfit) 
#    eloffAzdep[i] = eloff[i] - elFnElfit(pos,eldcfit,elsagfit) 


def onpick(event):
    thisline = event.artist
    xdata = thisline.get_xdata()
    ydata = thisline.get_ydata()
    ind = event.ind
    points = tuple(zip(xdata[ind], ydata[ind]))
    print('onpick points:', points)


elt = np.linspace(0,90,100)
azt = np.linspace(0,360,100)
post = (np.array(azt),np.array(elt))

# Figure 1: plots of corrected offsets vs az and el 
fig = plt.figure(figsize=(10,10))
#plt.style.use('classic')
grid = plt.GridSpec(4,4,hspace=0.3,wspace=0.3)

# Figure 5: plots of sky coverage and residuals
ax9 = fig.add_subplot(grid[0,0],projection='polar')
ax9.grid(color='black',linestyle='dotted',linewidth=1)
#ax9.set_xlabel('Azimuth (deg)',fontsize=10)
#ax9.set_ylabel('Elevation (deg)',fontsize=10)
#ax9.set_xlim(0,360)
#ax9.set_ylim(0,90)
r = 90-el
ax9.set_rmax(90)
ax9.plot(az,r,marker='o',markersize=3,linestyle='None',color='magenta')

#plotly_fig = tls.mpl_to_plotly(fig)
#plotly.offline.plot(plotly_fig)

ax10 = fig.add_subplot(grid[1,0])
ax10.set_xlabel('Azoff residuals (")',fontsize=10)
ax10.set_ylabel('Eloff residuals (")',fontsize=10)
ax10.set_xlim(-15,15)
ax10.set_ylim(-15,15)
ax10.xaxis.set_major_locator(MultipleLocator(10))
ax10.xaxis.set_minor_locator(MultipleLocator(5))
ax10.yaxis.set_major_locator(MultipleLocator(10))
ax10.yaxis.set_minor_locator(MultipleLocator(5))
ax10.yaxis.set_ticks_position('both')
ax10.xaxis.set_ticks_position('both')
ax10.set_aspect('equal')
ax10.plot(azres,elres,marker="+",markersize=6,linestyle='None',color='blue')
# 17.4 is the radius of a circle representing half width at half power
# for the 86 GHz beamsize (FWHM=69.5 arcsec)
# similarly scaled circle for 230 beam
#beam86=plt.Circle((0,0),17.4,color='orange',linewidth=2,fill=False)
#beam230=plt.Circle((0,0),8.7,color='red',linewidth=2,fill=False)
#ax2.add_artist(beam86)
#ax2.add_artist(beam230)
ax10.plot([0,0],[-15,15],color='grey',linestyle='dotted',linewidth=1)
ax10.plot([-15,15],[0,0],color='grey',linestyle='dotted',linewidth=1)

ax1 = fig.add_subplot(grid[0,2:])
ax1.grid(color='black',linestyle='dotted',linewidth=1)
ax1.set_xlabel('El (deg)',fontsize=10)
ax1.yaxis.set_label_position('right')
ax1.set_ylabel('El dep. Eloff (")',fontsize=10)
#ax1.text(55,eloffmax+3,elfitString)
ax1.set_xlim(0,90)
ax1.set_ylim(np.amin(eloffEldep)-10,np.amax(eloffEldep)+10)
ax1.xaxis.set_major_locator(MultipleLocator(30))
ax1.xaxis.set_minor_locator(MultipleLocator(10))
ax1.yaxis.set_major_locator(MultipleLocator(10))
ax1.yaxis.set_minor_locator(MultipleLocator(2))
ax1.yaxis.set_ticks_position('both')
ax1.xaxis.set_ticks_position('both')
ax1.errorbar(el,eloffEldep,yerr=elofferr,marker='o',markersize=3,linestyle='None',color='red')
ax1.plot(elt,elFnElfit(post,eldcfit,elsagfit),color='orange')

ax2 = fig.add_subplot(grid[1,2:])
ax2.grid(color='black',linestyle='dotted',linewidth=1)
ax2.yaxis.set_label_position('right')
ax2.set_ylabel('El dep. Azoff (")',fontsize=10)
#ax2.text(55,azoffmax+3,azfitString)
ax2.set_xlim(0,90)
ax2.set_ylim(np.amin(azoffEldep)-10,np.amax(azoffEldep)+10)
ax2.xaxis.set_major_locator(MultipleLocator(30))
ax2.xaxis.set_minor_locator(MultipleLocator(10))
ax2.yaxis.set_major_locator(MultipleLocator(10))
ax2.yaxis.set_minor_locator(MultipleLocator(2))
ax2.yaxis.set_ticks_position('both')
ax2.xaxis.set_ticks_position('both')
ax2.errorbar(el,azoffEldep,yerr=azofferr,marker='o',markersize=3,linestyle='None',color='red')
ax2.plot(elt,elFnAzfit(post,azdcfit,azcollfit,eltiltfit),color='orange')


ax3 = fig.add_subplot(grid[2,2:])
ax3.grid(color='black',linestyle='dotted',linewidth=1)
ax3.set_xlabel('Az (deg)',fontsize=10)
ax3.yaxis.set_label_position('right')
ax3.set_ylabel('Az dep. Eloff (")',fontsize=10)
#ax3.text(55,eloffmax+3,elfitString)
ax3.set_xlim(0,360)
ax3.set_ylim(np.amin(eloffAzdep)-10,np.amax(eloffAzdep)+10)
ax3.xaxis.set_major_locator(MultipleLocator(90))
ax3.xaxis.set_minor_locator(MultipleLocator(10))
ax3.yaxis.set_major_locator(MultipleLocator(10))
ax3.yaxis.set_minor_locator(MultipleLocator(2))
ax3.yaxis.set_ticks_position('both')
ax3.xaxis.set_ticks_position('both')
ax3.errorbar(az,eloffAzdep,yerr=elofferr,marker='o',markersize=3,linestyle='None',color='red')
ax3.plot(azt,azFnElfit(post,eaztltsinfit,eaztltcosfit,eaztltsin2fit,eaztltcos2fit),color='orange')

ax4 = fig.add_subplot(grid[3,2:])
ax4.grid(color='black',linestyle='dotted',linewidth=1)
ax4.set_ylabel('Az dep. Azoff (")',fontsize=10)
ax4.yaxis.set_label_position('right')
ax4.set_xlim(0,360)
ax4.set_ylim(np.amin(azoffAzdep)-10,np.amax(azoffAzdep)+10)
ax4.xaxis.set_major_locator(MultipleLocator(90))
ax4.xaxis.set_minor_locator(MultipleLocator(10))
ax4.yaxis.set_major_locator(MultipleLocator(10))
ax4.yaxis.set_minor_locator(MultipleLocator(2))
ax4.yaxis.set_ticks_position('both')
ax4.xaxis.set_ticks_position('both')
ax4.errorbar(az,azoffAzdep,yerr=azofferr,marker='o',markersize=3,linestyle='None',color='red')
ax4.plot(azt,azFnAzfit(post,aaztltsinfit,aaztltcosfit,aaztltsin2fit,aaztltcos2fit),color='orange')

# Figure 4: plots of raw offsets vs az and el 
ax5 = fig.add_subplot(grid[2,0])
ax5.grid(color='black',linestyle='dotted',linewidth=1)
ax5.set_ylabel('Azimuth offsets (")',fontsize=10)
ax5.set_xlim(0,360)
ax5.set_ylim(np.amin(azoff)-10,np.amax(azoff)+10)
ax5.xaxis.set_major_locator(MultipleLocator(90))
ax5.xaxis.set_minor_locator(MultipleLocator(10))
ax5.yaxis.set_major_locator(MultipleLocator(10))
ax5.yaxis.set_minor_locator(MultipleLocator(2))
ax5.yaxis.set_ticks_position('both')
ax5.xaxis.set_ticks_position('both')
ax5.errorbar(az,azoff,yerr=azofferr,marker='x',markersize=5,linestyle='None',color='red')
ax5.plot(az,azres,marker='+',markersize=3,linestyle='None',color='blue')

ax6 = fig.add_subplot(grid[2,1])
ax6.set_xlim(0,90)
ax6.grid(color='black',linestyle='dotted',linewidth=1)
ax6.set_ylim(np.amin(azoff)-10,np.amax(azoff)+10)
ax6.xaxis.set_major_locator(MultipleLocator(30))
ax6.xaxis.set_minor_locator(MultipleLocator(10))
ax6.yaxis.set_major_locator(MultipleLocator(10))
ax6.yaxis.set_minor_locator(MultipleLocator(2))
ax6.set_yticklabels([])
ax6.yaxis.set_ticks_position('both')
ax6.xaxis.set_ticks_position('both')
ax6.errorbar(el,azoff,yerr=azofferr,marker='x',markersize=5,linestyle='None',color='red')
ax6.plot(el,azres,marker='+',markersize=3,linestyle='None',color='blue')

ax7 = fig.add_subplot(grid[3,0])
ax7.grid(color='black',linestyle='dotted',linewidth=1)
ax7.set_xlabel('Az (deg)',fontsize=10)
ax7.set_ylabel('Elevation offsets (")',fontsize=10)
ax7.set_xlim(0,360)
ax7.set_ylim(np.amin(eloff)-10,np.amax(eloff)+10)
ax7.xaxis.set_major_locator(MultipleLocator(90))
ax7.xaxis.set_minor_locator(MultipleLocator(10))
ax7.yaxis.set_major_locator(MultipleLocator(10))
ax7.yaxis.set_minor_locator(MultipleLocator(2))
ax7.yaxis.set_ticks_position('both')
ax7.xaxis.set_ticks_position('both')
ax7.errorbar(az,eloff,yerr=elofferr,marker='x',markersize=5,linestyle='None',color='red')
ax7.plot(az,elres,marker='+',markersize=3,linestyle='None',color='blue')

ax8 = fig.add_subplot(grid[3,1])
ax8.grid(color='black',linestyle='dotted',linewidth=1)
ax8.set_xlabel('El (deg)',fontsize=10)
ax8.set_xlim(0,90)
ax8.set_ylim(np.amin(eloff)-10,np.amax(eloff)+10)
ax8.xaxis.set_major_locator(MultipleLocator(30))
ax8.xaxis.set_minor_locator(MultipleLocator(10))
ax8.yaxis.set_major_locator(MultipleLocator(10))
ax8.yaxis.set_minor_locator(MultipleLocator(2))
ax8.set_yticklabels([])
ax8.yaxis.set_ticks_position('both')
ax8.xaxis.set_ticks_position('both')
ax8.errorbar(el,eloff,yerr=elofferr,marker='x',markersize=5,linestyle='None',color='red')
ax8.plot(el,elres,marker='+',markersize=3,linestyle='None',color='blue')

resultsString = ""
resultsFile = open('results','r')
for line in resultsFile:
    line = line.strip()
    resultsString = resultsString+line+'\n'
resultsFile.close()

props = dict(boxstyle='round',facecolor='wheat',alpha=0.5)

ax11 = fig.add_subplot(grid[0:1,1])
ax11.axis('off')
ax11.set_title(plottitle)
ax11.text(-0.1,0.85,resultsString,fontsize=9,transform=ax11.transAxes,verticalalignment='top',bbox=props)

#plotly_fig = tls.mpl_to_plotly(fig)
#plotly.offline.plot(plotly_fig)
plt.savefig('fig1.pdf')
plt.show()
plt.ioff()
