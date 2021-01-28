#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Revised by Satoki Mar.6 2018 from the rscan_pfit2.py by Locutus Dec. 2017
# Python 3.5 Ubuntu 16.04
"""
Plot and Gaussian-fit the continuum recording data of radio source scan, to 
derive the pointing error.

CSV data columns: time, az (deg), azoff (arcsec), az_error (arcsec), 
                   el, eloff, el_error, contR (mV) and contL
"""

import sys

#def eff(csvname, T_hot, T_amb, T_atm, size, freq, tau_z, axi='az'):
def eff(csvname, size, tau_z, axi='az'):
    """
    parameter axi: can be either of 'az', 'el', 'auto'.
    """

    import numpy as np
    from matplotlib import pyplot as plt
    from scipy.optimize import curve_fit
    from scipy.stats import norm
    
    check_here = True

    Area   = 1130973.4  ### 12-m area cm^2
    #T_sky = T_hot * (1.0 - np.exp(-tau))
    T_cmbr = 2.7
    # read the CSV file
    """
    import pandas as pd
    colnames = ['time', 'az', 'azoff', 'azerr', 'el', 'eloff', 'elerr', 'contR', 'contL']
    df = pd.read_csv(csvname, sep=',', header=None, names=colnames)
    df.time = [pd.to_datetime(x, format='%y%m%d_%H%M%S.%f') for x in df.time]
    print(df.time)
    """
    #cols: 'time', 'az', 'azoff', 'azerr', 'el', 'eloff', 'elerr', 'freq', 'T_atm', 'T_amb', 'PM_R', 'PM_L'
    df = np.genfromtxt(csvname, delimiter=',', usecols=np.arange(1,12,1))
    ax = {'az':0, 'el':3}
 
    # determine the scan axis
        #*# Note the other axis coord. still changes, because of az axis tilt?
    if axi == 'auto':   # check which axis has all zero offsets
        if np.all(df[:,1]<1e-20) and np.any(df[:,4]!=0):
            axi = 'el'
        elif np.all(df[:,4]<1e-20) and np.any(df[:,1]!=0):
            axi = 'az'
        else:
            axi = input("Cannot decide. Manually select the scan axis 'az' or 'el' here: ")
    if axi not in ['az', 'el']:
        raise SystemExit('Improper scan axis. Exit.')

    # find the targeted source poistion (where offset=0)
    if (df[:,ax[axi]+1]==0).any() == True:
        print('Find zero point.')
        off0_scan = np.mean(df[df[:,ax[axi]+1]==0, 0:4:3], axis=0)
    else:
        print('Could not find zero point. Condition relaxed.')
        off0_scan = np.mean(df[df[:,ax[axi]+1]<2, 0:4:3], axis=0)
    print('zero offset at az = {}, el = {}, along the {} axis'.format(*off0_scan, axi))

    # remove off-src
    #if not check_here: #**************************? disabled befause of gltTrack slow refresh rate
    #    track_thres = 1      # arcsec
    #    el_dis = np.sum(df[:,4:6], axis=1, keepdims=False)
    #    el_all = df[:,3] + el_dis/3600
    #    df = df[np.logical_and(np.fabs(df[:,2]) *np.cos(el_all /180 *np.pi) < # project δAz to δφ
    #                           track_thres, np.fabs(df[:,5]) < track_thres)]
    
    azel_dis = {'az':np.sum(df[:,1:2], axis=1, keepdims=False), 
                'el':np.sum(df[:,4:5], axis=1, keepdims=False)}  # arcsec
    #azel_all = {'az':df[:,0] + azel_dis['az']/3600, 
    #            'el':df[:,3] + azel_dis['el']/3600}              # degree
    el_ave = np.mean(df[:,3])
 
    freq  = np.mean(df[:,6]) + 5.0   ### Assuming USB.
    T_atm = np.mean(df[:,7])
    T_hot = np.mean(df[:,8])
    T_amb = T_atm

    axname = {'az':'Azimuth', 'el':'Elevation'}
    #plt.figure(1)
    #plt.title('scan tracjectory')
    #plt.plot(azel_all['az'], azel_all['el'], '.')
    #plt.xlabel('Az (deg)')
    #plt.ylabel('El (deg)')
    #plt.grid(True)

    hot_pos_R = []
    hot_amp_R = []
    source_pos_R = []
    source_amp_R = []
    hot_pos_L = []
    hot_amp_L = []
    source_pos_L = []
    source_amp_L = []
    for i in range(len(azel_dis[axi])):
        if df[i,9] > 0.99*max(df[:,9]):
            hot_pos_R.append(azel_dis[axi][i])
            hot_amp_R.append(df[i,9])
        if df[i,10] > 0.99*max(df[:,10]):
            hot_pos_L.append(azel_dis[axi][i])
            hot_amp_L.append(df[i,10])
        #if df[i,6] < 1.02*min(df[:,6]):
        if (azel_dis[axi][i] > 0.95 * min(hot_pos_R)) and (azel_dis[axi][i] < abs(0.95 * max(hot_pos_R))):
            source_pos_R.append(azel_dis[axi][i])
            source_amp_R.append(df[i,9])
        #if df[i,7] < 10.0*min(df[:,7]):
        if (azel_dis[axi][i] > 0.95 * min(hot_pos_L)) and (azel_dis[axi][i] < abs(0.95 * max(hot_pos_L))):
            source_pos_L.append(azel_dis[axi][i])
            source_amp_L.append(df[i,10])
    #print(max(df[:,6]),min(df[:,6]))
    #print(hot_pos_R)
    #print(hot_amp_R)
    #print(source_pos_R)
    #print(source_amp_R)

    # 1D Gaussian-fit along the projected axis; doesn't matter in peak finding
    def gaussian(x, mean, sig, amp, dc):
    #def gaussian(x, mean, sig, amp, b, dc):
        return amp * np.exp(-(x-mean)**2/(2*sig**2)) + dc
        #return amp * np.exp(-(x-mean)**2/(2*sig**2)) + b * x + dc

    # plot az+ or el+off (projected axis) vs. powers
    if axi == 'az':
        plt.figure
        plt.subplot(3, 2, 1)
        plt.plot(azel_dis[axi], df[:,9],'.', label='contR')
        plt.ylabel('RHC Power (mW)')
        plt.grid(True)

        plt.figure
        plt.subplot(3, 2, 3)
        #plt.title('Power vs. Scan axis with Gaussian fit')
        plt.plot(hot_pos_R, hot_amp_R,'.', label='hotR')
        plt.ylabel('RHC Power (mW)')
        plt.grid(True)
 
        plt.subplot(3, 2, 5)
        plt.plot(source_pos_R, source_amp_R,'.', label='contR')
        plt.ylabel('RHC Power (mW)')
        plt.grid(True)
 
        plt.figure
        plt.subplot(3, 2, 2)
        plt.plot(azel_dis[axi], df[:,10],'.', label='contL')
        plt.ylabel('LHC Power (mW)')
        plt.grid(True)

        plt.subplot(3, 2, 4)
        plt.plot(hot_pos_L, hot_amp_L,'.', label='hotL')
        plt.ylabel('LHC Power (mW)')
        plt.grid(True)
 
        plt.subplot(3, 2, 6)
        plt.plot(source_pos_L, source_amp_L,'.', label='contL')
        plt.ylabel('LHC Power (mW)')
        plt.grid(True)
 
        #df_ave = (df[:,6] + df[:,7]) / 2.0
        #plt.subplot(3, 1, 3)
        #plt.plot(azel_dis[axi], df_ave, '.', label='Integ.R+L')
        #plt.ylabel('R+L Power (mW)')
        #plt.xlabel(axname[axi] + ' Offset (arcsec)')
        #plt.grid(True)

        sig0 = np.ptp(source_pos_R) /6
            # initial guess of sigma - assume the scan covers 4σ ~ 99%
        x0 = np.mean(source_pos_R, axis=0)
        dc0 = np.mean(source_amp_R, axis=0)
        a0 = (np.amax(source_amp_R, axis=0) - dc0) #* sig0 * np.sqrt(2*np.pi)
        xmax = len(source_pos_R)-1
        b0 = (source_amp_R[xmax] - source_amp_R[0]) / (source_pos_R[xmax] - source_pos_R[0])
        #b0 = (df[xmax,6] - df[0,6]) / (azel_dis[axi][xmax] - azel_dis[axi][0])
        print('Gaussian-fit initial guesses: sigma=', sig0, 'amp=', a0, 'b=', b0, 'dc=', dc0)
        #poptR, pcovR = curve_fit(gaussian, azel_dis[axi], df[:,6], p0=(0, sig0, a0[0], dc0[0]))
        poptR, pcovR = curve_fit(gaussian, source_pos_R, source_amp_R, p0=(x0, sig0, a0, dc0))
        #poptR, pcovR = curve_fit(gaussian, source_pos_R, source_amp_R, p0=(x0, sig0, a0, b0, dc0))
        print('RHC fit: mean= {}, sigma= {}, amp={}, dc= {}'.format(*poptR))
        #print('RHC fit: mean= {}, sigma= {}, amp={}, b={}, dc= {}'.format(*poptR))
        #poptL, pcovL = curve_fit(gaussian, azel_dis[axi], df[:,7], p0=(x0, sig0, a0, b0, dc0))
        poptL, pcovL = curve_fit(gaussian, source_pos_L, source_amp_L, p0=(x0, sig0, a0, dc0))
        #poptL, pcovL = curve_fit(gaussian, source_pos_L, source_amp_L, p0=(x0, sig0, a0, b0, dc0))
        print('LHC fit: mean= {}, sigma= {}, amp={}, dc= {}'.format(*poptL))
        #print('LHC fit: mean= {}, sigma= {}, amp={}, b={}, dc= {}'.format(*poptL))
        #poptRL, pcovRL = curve_fit(gaussian, azel_dis[axi], df_ave, p0=(x0, sig0, a0, b0, dc0))
        #print('R+L fit: mean= {}, sigma= {}, amp={}, b={}, dc= {}'.format(*poptRL))
 
        # overlay with the fit
        #plt.subplot(3, 1, 1)
        #plt.plot(azel_dis[axi], gaussian(azel_dis[axi], *poptR))
        plt.subplot(3, 2, 5)
        plt.plot(source_pos_R, gaussian(source_pos_R, *poptR))
        plt.subplot(3, 2, 6)
        plt.plot(source_pos_L, gaussian(source_pos_L, *poptL))
        #plt.plot(azel_dis[axi], gaussian(azel_dis[axi], *poptRL))

        ### hotload_amp_R = V_hot - V_sky
        ave_hot_amp_R = np.mean(hot_amp_R)
        ave_hot_amp_L = np.mean(hot_amp_L)
        V_sky_R = poptR[3]
        V_sky_L = poptL[3]
        hotload_amp_R = np.mean(hot_amp_R) - poptR[3]
        hotload_amp_L = np.mean(hot_amp_L) - poptL[3]

        ### FWHM
        fwhm_R = 2.0*np.sqrt(2.0*np.log(2.0))*poptR[1]
        fwhm_L = 2.0*np.sqrt(2.0*np.log(2.0))*poptL[1]

        print('')
        print('AZ offset    [RHC]:', poptR[0], '[arcsec]')
        print('AZ FWHM      [RHC]:', fwhm_R, '[arcsec]')
        print('Hotload Amp. [RHC]:', hotload_amp_R, '[mW]')
        print('Source Amp.  [RHC]:', poptR[2], '[mW]')
        print('')
        print('AZ offset    [LHC]:', poptL[0], '[arcsec]')
        print('AZ FWHM      [LHC]:', fwhm_L, '[arcsec]')
        print('Hotload Amp. [LHC]:', hotload_amp_L, '[mW]')
        print('Source Amp.  [LHC]:', poptL[2], '[mW]')
        #print('')
        #print('AZ = {}, EL = {}'.format(*off0_scan))
        #print('AZ offset [R+L]:', poptRL[0], 'arcsec')
        #print('AZ FWHM   [R+L]:', 2.0*np.sqrt(2.0*np.log(2.0))*poptRL[1], 'arcsec')
        print('')


    if axi == 'el':
        plt.figure
        plt.subplot(3, 1, 1)
        plt.plot(azel_dis[axi], df[:,8], '.', label='contR')
        plt.ylabel('RHC Power (mW)')
        plt.grid(True)

        plt.subplot(3, 1, 2)
        plt.plot(azel_dis[axi], df[:,9], '.', label='contL')
        plt.ylabel('LHC Power (mW)')
        plt.grid(True)

        df_ave = (df[:,8] + df[:,9]) / 2.0
        plt.subplot(3, 1, 3)
        plt.plot(azel_dis[axi], df_ave, '.', label='Integ.R+L')
        plt.ylabel('R+L Power (mW)')
        plt.xlabel(axname[axi] + ' Offset (arcsec)')
        plt.grid(True)

        sig0 = np.ptp(azel_dis[axi]) /6
        x0 = np.mean(azel_dis[axi], axis=0)
        dc0 = np.mean(df[:,8], axis=0)
        a0 = (np.amax(df[:,8], axis=0) - dc0) #* sig0 * np.sqrt(2*np.pi)
        xmax = azel_dis[axi].shape[0] - 1
        b0 = (df[xmax,8] - df[0,8]) / (azel_dis[axi][xmax] - azel_dis[axi][0])
        print('Gaussian-fit initial guesses: sigma=', sig0, 'amp=', a0, 'b=', b0, 'dc=', dc0)
        poptR, pcovR = curve_fit(gaussian, azel_dis[axi], df[:,8], p0=(x0, sig0, a0, b0, dc0))
        print('RHC-fit: mean= {}, sigma= {}, amp={}, b={}, dc= {}'.format(*poptR))
        poptL, pcovL = curve_fit(gaussian, azel_dis[axi], df[:,9], p0=(x0, sig0, a0, b0, dc0))
        print('LHC-fit: mean= {}, sigma= {}, amp={}, b={}, dc= {}'.format(*poptL))
        poptRL, pcovRL = curve_fit(gaussian, azel_dis[axi], df_ave, p0=(x0, sig0, a0, b0, dc0))
        print('R+L fit: mean= {}, sigma= {}, amp={}, b={}, dc= {}'.format(*poptRL))

        plt.subplot(3, 1, 1)
        plt.plot(azel_dis[axi], gaussian(azel_dis[axi], *poptR))
        plt.subplot(3, 1, 2)
        plt.plot(azel_dis[axi], gaussian(azel_dis[axi], *poptL))
        plt.subplot(3, 1, 3)
        plt.plot(azel_dis[axi], gaussian(azel_dis[axi], *poptRL))
        #plt.legend()

        print('')
        print('EL offset [RHC]:', poptR[0], 'arcsec')
        print('EL FWHM   [RHC]:', 2.0*np.sqrt(2.0*np.log(2.0))*poptR[1], 'arcsec')
        print('EL offset [LHC]:', poptL[0], 'arcsec')
        print('EL FWHM   [LHC]:', 2.0*np.sqrt(2.0*np.log(2.0))*poptL[1], 'arcsec')
        print('')
        print('AZ = {}, EL = {}'.format(*off0_scan))
        print('EL offset [R+L]:', poptRL[0], 'arcsec')
        print('EL FWHM   [R+L]:', 2.0*np.sqrt(2.0*np.log(2.0))*poptRL[1], 'arcsec')
        print('')

    plt.show()
    
    ##### From here, most of the calculations are adopted from SMA
    #####   aperEff.c written by TKS, Nimesh, and Todd

    ### Theoretical beam size
    beam = 1.12 * (0.299792 / freq) / 12.0 * (180.0 * 3600.0) / np.pi
    ### Devonvolved beam size
    beam_R = np.sqrt(fwhm_R**2 - size**2)
    beam_L = np.sqrt(fwhm_L**2 - size**2)

    print('Theoretical beam size   =', beam, '[arcsec]')
    print('Deconv. Beam size [RHC] =', beam_R, '[arcsec]')
    print('Deconv. Beam size [LHC] =', beam_L, '[arcsec]')
    print('Source size   =', size, '[arcsec]')

    ### Brightness Temperature for Mars
    if ((freq > 60.0) and (freq < 118.0)):
        T_sbt = 206.8  ### [K]  <== Brightness temperature at 90 GHz.
                       ###          Ulich 1981, AJ, 86, 1619
        eta_l = 0.945
    elif ((freq > 118.0) and (freq < 200.0)):
        T_sbt = 206    ### [K]  <== Brightness temperature at 150 GHz.
                       ###          Ulich 1981, AJ, 86, 1619
    elif ((freq > 200.0) and (freq < 300)):
        T_sbt = 225    ### [K]  <== Brightness temperature at 214 GHz.
                       ###          Rather et al. 1974, Icarus, 23, 448
        eta_l = 0.922
    print('Source Temp.  =', T_sbt, '[K]')

    print('Hotload Temp. =', T_hot, '[K]')
    print('Atmos.  Temp. =', T_atm, '[K]')
    print('Ambient Temp. =', T_amb, '[K]')
    #print('Sky Temp.     =', T_sky, '[K]')
    print('')

    ### R-J brightness temperature definition is assumed; 
    ###   but not R-J approximation
    J_cmbr = 1.0 / (np.exp(0.048 * freq / T_cmbr) - 1.0)
    J_hot  = 1.0 / (np.exp(0.048 * freq / (T_hot)) - 1.0)
    J_amb  = 1.0 / (np.exp(0.048 * freq / (T_amb)) - 1.0)
    J_atm  = 1.0 / (np.exp(0.048 * freq / (T_atm)) - 1.0)

    #J_sbt = T_sbt / (0.048 * freq)
    tau = tau_z / np.cos((90.0 - el_ave) * np.pi / 180.0)

    print('Average EL       =', el_ave, '[deg]')
    print('Tau @ average EL =', tau)
    print('')

    ### f is the correction factor for the beam-profile and source size;
    ###   the "source coupling efficiency"
    ### could in principle incorporate specific source structure, etc.

    ### Using the deconvolved beam size
    f0_R = (size/beam_R)**2 * np.log(2.0)
    f0_L = (size/beam_L)**2 * np.log(2.0)
    ### Using the theoretical beam size
    #f0_R = (size/beam)**2 * np.log(2.0)
    #f0_L = (size/beam)**2 * np.log(2.0)

    f_R  = (1.0 - np.exp(-f0_R)) / f0_R
    f_L  = (1.0 - np.exp(-f0_L)) / f0_L

    print('Source Coupling Efficiency =', f_R, f_L)
    print('Forward Spillover & Scattering Efficiency =', eta_l)
    print('')

    ### Correction factor for CMBR contribution

    f_cmbr_R = np.exp(-f0_R)
    f_cmbr_L = np.exp(-f0_L)

    J_cal = J_hot * (np.exp(tau) * (1.0 - eta_l * J_atm / J_hot
                                    - (1.0 - eta_l) * J_amb / J_hot)
                     + eta_l * (J_atm - J_cmbr) / J_hot) / eta_l

    ### Ratio gives the source strength when scaled by
    ###   Tcal = Thot = Tatm = Tamb
    ### in the simple 0th order approach,
    ### so-called chopper-wheel calibration of Penzias & Burrus fame.
    ### All the corrections are incorporated into a modified Tcal or Jcal
    ### in the non-R-J case

    ### poptR[2] = V_on - V_sky

    ratio_R = poptR[2] / hotload_amp_R
    ratio_L = poptL[2] / hotload_amp_L
    J_source_R = ratio_R * J_cal - (f_cmbr_R - 1.0) * J_cmbr
    J_source_L = ratio_L * J_cal - (f_cmbr_L - 1.0) * J_cmbr
    T_source_R = 0.048 * freq / np.log(1.0 / J_source_R + 1.0)
    T_source_L = 0.048 * freq / np.log(1.0 / J_source_L + 1.0)
    T_source_RJ_R = 0.048 * freq * J_source_R
    T_source_RJ_L = 0.048 * freq * J_source_L

    T_cal = 0.048 * freq / np.log(1.0 / J_cal + 1.0)

    ### Ta* = (V_on - V_sky)/(V_hot - V_sky) * T_amb
    ### poptR[2] = V_on - V_sky
    #Ta_source_R = poptR[2] / hotload_amp_R * T_hot
    #Ta_source_L = poptL[2] / hotload_amp_L * T_hot

    #print('Source Temp. [RHC] =', Ta_source_R, '[K]')
    #print('Source Temp. [LHC] =', Ta_source_L, '[K]')
    print('Source Temp. [RHC] =', T_source_RJ_R, '[K]')
    print('Source Temp. [LHC] =', T_source_RJ_L, '[K]')

    #T_source_dilute = T_source * (size**2 / beam**2)

    #Eff_R = Ta_source_R / T_source_dilute
    #Eff_L = Ta_source_L / T_source_dilute

    Lambda = 30 / freq  ### [cm]
    OmegaS = np.pi * (size/2.0)**2 * 2.35 * 10**(-11)

    EtaA_R = T_source_RJ_R * Lambda**2 / (T_sbt * f_R * Area * OmegaS)
    EtaA_L = T_source_RJ_L * Lambda**2 / (T_sbt * f_L * Area * OmegaS)
    EtaB_R = T_source_RJ_R / (T_sbt * f_R)
    EtaB_L = T_source_RJ_L / (T_sbt * f_L)

    #print('Efficiency [RHC] =', Eff_R * 100, '[%]')
    #print('Efficiency [LHC] =', Eff_L * 100, '[%]')
    print('Aperture  Efficiency [RHC] =', EtaA_R * 100, '[%]')
    print('Aperture  Efficiency [LHC] =', EtaA_L * 100, '[%]')
    print('Main Beam Efficiency [RHC] =', EtaB_R * 100, '[%]')
    print('Main Beam Efficiency [LHC] =', EtaB_L * 100, '[%]')

    ## derive the pointing error
    #if check_here:  # *********************************************? because LHC not ready
    #    poptL = poptR 
    #print('Az = {}, El = {} (deg), pointing error = {} (arcsec) along the {} axis.'.format(
    #      *off0_scan, np.mean((poptR[0], poptL[0])), axi))


csvfile = sys.argv[1]
#T_hot = sys.argv[2]

### For measurement data "contData_190125_180257_Rx230_Mars+hotload"
#T_hot = 282.83  ### [K]
#T_atm = 252.15  ### [K]
#T_amb = 285.48  ### [K]
#size = 6.36   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.14  ### Zenith opacity

### For measurement data "contData_190125_185220_Rx230_Mars+hotload"
#T_hot = 282.79  ### [K]
#T_atm = 252.15  ### [K]
#T_amb = 285.10  ### [K]
#size = 6.36   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.13  ### Zenith opacity

### For measurement data "contData_190126_195317_Rx230_Mars+hotload"
#T_hot = 282.79  ### [K]
#T_atm = 252.15  ### [K]
#T_amb = 285.10  ### [K]
#size = 6.32   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.11  ### Zenith opacity

### For measurement data "contData_190126_210347_Rx230_Mars+hotload"
#T_hot = 279.81  ### [K]
#T_atm = 241.75  ### [K]
#T_amb = 283.46  ### [K]
#size = 6.32   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.10  ### Zenith opacity

### For measurement data "contData_190127_224251_Rx230_Mars+hotload"
#T_hot = 281.42  ### [K]
#T_atm = 245.25  ### [K]
#T_amb = 284.32  ### [K]
#size = 6.28   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.14  ### Zenith opacity

### For measurement data "contData_190128_175617_Rx230_Mars+hotload"
#T_hot = 280.93  ### [K]
#T_atm = 249.05  ### [K]
#T_amb = 283.95  ### [K]
#size = 6.25   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.14  ### Zenith opacity

### For measurement data "contData_190128_183306_Rx230_Mars+hotload"
#T_hot = 280.97  ### [K]
#T_atm = 247.55  ### [K]
#T_amb = 284.19  ### [K]
#size = 6.25   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.13  ### Zenith opacity

### For measurement data "contData_190128_191521_Rx230_Mars+hotload"
#T_hot = 281.01  ### [K]
#T_atm = 248.25  ### [K]
#T_amb = 284.41  ### [K]
#size = 6.25   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.14  ### Zenith opacity

### For measurement data "contData_190128_194057_Rx230_Mars+hotload"
#T_hot = 280.98  ### [K]
#T_atm = 247.13  ### [K]
#T_amb = 284.41  ### [K]
#size = 6.25   ### [arcsec]
#freq = 230.010   ### [GHz]
#tau_z = 0.14  ### Zenith opacity

#T_hot = 286.31  ### [K]
#T_atm = 160  ### [K]
#T_amb = 180  ### [K]
#size = 4.6   ### [arcsec]
#freq = 86.2   ### [GHz]
#tau_z = 0.08  ### Zenith opacity

### For measurement data "EfficiencyData_20201110_032215_Rx86_mars"
### For measurement data "EfficiencyData_20201110_035002_Rx86_mars"
### For measurement data "EfficiencyData_20201110_041642_Rx86_mars"
### For measurement data "EfficiencyData_20201110_043406_Rx86_mars"
size = 18.4   ### [arcsec]
tau_z = 0.068  ### Zenith opacity

### For measurement data "EfficiencyData_20201110_060011_Rx86_mars"
### For measurement data "EfficiencyData_20201110_062134_Rx86_mars"
### For measurement data "EfficiencyData_20201110_064005_Rx86_mars"
#size = 18.4   ### [arcsec]
#tau_z = 0.067  ### Zenith opacity


#eff(csvfile, T_hot, T_amb, T_atm, size, freq, tau_z)
eff(csvfile, size, tau_z)
