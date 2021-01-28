#!/usr/bin/env pythonw

import ephem as ep
import math
import numpy
import string
import time
import ast
import wx
#import wx.lib.buttons as B
import wx.lib.agw.gradientbutton as GB
#import wx.lib.agw.aquabutton as AB

class MainFrame(wx.Frame):
    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(1080, 768))
        self.cpanel = CtrlPanel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(self.cpanel, 0, wx.EXPAND)
        vbox.Add((-1, 6))

        self.SetSizerAndFit(vbox)
        self.Centre()
        self.Show()

    def goodbye(self, evt):
        self.Close()

# end of class MainFrame

class CtrlPanel(wx.Panel):
    def __init__(self, parent):
        self.mf = parent
        wx.Panel.__init__(self, parent, -1)
        vbox1 = wx.BoxSizer(wx.VERTICAL)
        hbox1 = wx.BoxSizer(wx.HORIZONTAL)
        hbox1A = wx.BoxSizer(wx.HORIZONTAL)
        hbox2 = wx.BoxSizer(wx.HORIZONTAL)
        hbox2A = wx.BoxSizer(wx.HORIZONTAL)
        hbox3 = wx.BoxSizer(wx.HORIZONTAL)
        hbox4 = wx.BoxSizer(wx.HORIZONTAL)
        hbox5 = wx.BoxSizer(wx.HORIZONTAL)

        verfont = wx.Font(8, wx.DEFAULT, wx.ITALIC, wx.NORMAL)
        self.version = wx.StaticText(self, label="VLSR 1.00")
        self.version.SetFont(verfont)

        self.chat = False

        self.sunlong = 270.0
        self.dtup = (2013, 12, 21, 17, 10, 53)
        self.epd = ep.Date(self.dtup)
        st1 = wx.StaticText(self, label='Measurement Date (year/mon/day): ')
        st1a = wx.StaticText(self, label=' UTC')
        self.st1b = wx.StaticText(self, label='')
        self.tc1 = wx.TextCtrl(self, value='0.0', size=(96, -1), style=wx.TE_PROCESS_ENTER)
        self.tc1.SetValue('2013/12/21')
        self.tc1.Bind(wx.EVT_TEXT_ENTER, self.manage_date)
        st2 = wx.StaticText(self, label='Measurement Time (hr:min:sec): ')
        st2a = wx.StaticText(self, label=' UTC')
        st2b = wx.StaticText(self, label='Sun Ecliptic Longitude: ')
        self.tc2 = wx.TextCtrl(self, value='0.0', size=(96, -1), style=wx.TE_PROCESS_ENTER)
        self.tc2.SetValue('17:10:53')
        self.tc2.Bind(wx.EVT_TEXT_ENTER, self.manage_time)
        self.tc3 = wx.TextCtrl(self, -1, style=wx.TE_READONLY, size=(108,-1))

        self.scope = ep.Observer()
        self.scope.lat = ep.degrees("42:21:38.67")
        self.scope.long = ep.degrees("-71:05:27.84")
        self.scope.pressure = 0
        self.scope.elevation = 30

        self.tndict = dict()
        tnlist = [
            {'Sun':'#:Sun'},
            {'Mars':'#:Mars'},
            {'Moon':'#:Moon'},
            {'Jupiter':'#:Jupiter'},
            {'Stow':'#:EQDC:0.0:0.0'},
            {'Andromeda':'Andromeda,f|D|B9,0:8:23.26|135.67,29:5:25.55|-163,2.06,2000'},
            {'Cassiopeiae':'Alpha Cassiopeiae,f|D|K0,0:40:30.44|50.37,56:32:14.39|-32.2,2.25,2000'},
            {'Crab Nebula':'Crab Nebula,f|R,5:34:31.9,22:0:52,8.4,2000,360'},
            {'Vega':'Vega,f,18:36:56,38:47,0.04,2000'},
            ]
        for line in tnlist:
            try:
                #tmp = eval(line)
                #k = tmp.keys()
                self.tndict.update(line)
            except ValueError as e:
                pass

        self.tlbl = wx.StaticText(self, -1, "Choose Target:")
        self.tts = []
        self.tts.append("HA, DC")
        self.tts.append("AZ, EL")
        self.tts.append("Glon, Glat")
        self.tts.append("RA, DEC")
        for k in self.tndict.keys():
            self.tts.append(k)
        self.set_tt = wx.Choice(self, choices=self.tts)
        self.set_tt.Bind(wx.EVT_CHOICE, self.getTargType)
        self.set_tt.SetSelection(0)
        self.ttext = wx.TextCtrl(self, -1, style=wx.TE_PROCESS_ENTER,
                size=(324,-1))
        self.ttext.Bind(wx.EVT_TEXT_ENTER, self.onTargEnter)

        self.targ_lbl = wx.StaticText(self, -1, "Target:")
        self.lblhadc = wx.StaticText(self, -1, "HADC")
        self.lblazel = wx.StaticText(self, -1, "AZEL")
        self.lblgala = wx.StaticText(self, -1, "Galactic")
        self.lbleclp = wx.StaticText(self, -1, "Ecliptic")
        self.lblradc = wx.StaticText(self, -1, "Target RADC: ")
        self.text_ha_aim = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        self.text_az_aim = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        self.text_ga_aim = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        self.text_ec_aim = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        self.text_radc = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(320,-1))
        self.now_cb = wx.CheckBox(self, style=wx.CHK_2STATE, label='Use Current Time ')
        self.now_cb.Bind(wx.EVT_CHECKBOX, self.use_current)
        self.now_cb.SetValue(False)

        self.calcbut = wx.Button(self, wx.ID_ANY, label="Calculate VLSR")
        self.calcbut.SetToolTip(wx.ToolTip("click to calculate VLSR"))
        self.calcbut.Bind(wx.EVT_BUTTON, self.calculate)
        q_button = GB.GradientButton(self, label='Quit', size=(70, 30))
        q_button.SetForegroundColour(wx.RED)
        q_button.Bind(wx.EVT_BUTTON, self.mf.goodbye)

        st4 = wx.StaticText(self, label='Vsun: ')
        self.text_vsun = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        st5 = wx.StaticText(self, label='Vorb: ')
        self.text_vorb = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        st6 = wx.StaticText(self, label='VLSR: ')
        self.text_vlsr = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(108,-1))
        st7 = wx.StaticText(self, label='Zero LSR Red Shift: ')
        self.text_zrs = wx.TextCtrl(self, -1, style=wx.TE_READONLY,
                size=(128,-1))


        hbox1.Add((8,-1), 0)
        hbox1.Add(st1, 0)
        hbox1.Add(self.tc1, 0)
        hbox1.Add(st1a, 0)
        hbox1.Add((12,-1), 0)
        hbox1.Add(self.st1b, 0)
        hbox1.AddStretchSpacer()
        hbox1.Add(q_button, 0, wx.TOP, 5)
        hbox1.Add((24, -1), 0)

        hbox1A.Add((8,-1), 0)
        hbox1A.Add(st2, 0)
        hbox1A.Add(self.tc2, 0)
        hbox1A.Add(st2a, 0)
        hbox1A.Add((48,-1), 0)
        hbox1A.Add(st2b, 0)
        hbox1A.Add(self.tc3, 0)
        hbox1A.AddStretchSpacer()


        hbox2.Add((8,-1), 0)
        hbox2.Add(self.targ_lbl, 0)
        hbox2.Add((10, -1), 0)
        hbox2.Add(self.text_ha_aim, 0)
        hbox2.Add(self.lblhadc, 0)
        hbox2.Add((10, -1), 0)
        hbox2.Add(self.text_az_aim, 0)
        hbox2.Add(self.lblazel, 0)
        hbox2.Add((10, -1), 0)
        hbox2.Add(self.text_ga_aim, 0)
        hbox2.Add(self.lblgala, 0)
        hbox2.Add((10, -1), 0)
        hbox2.Add(self.text_ec_aim, 0)
        hbox2.Add(self.lbleclp, 0)
        hbox2.AddStretchSpacer()

        hbox2A.Add((8,-1), 0)
        hbox2A.Add(self.lblradc, 0)
        hbox2A.Add(self.text_radc, 0)
        hbox2A.Add((132,-1), 0)
        hbox2A.Add(self.now_cb, 0)
        hbox2.AddStretchSpacer()

        hbox3.Add((8, -1), 0)
        hbox3.Add(self.tlbl, 0)
        hbox3.Add((10, -1), 0)
        hbox3.Add(self.set_tt, 0)
        hbox3.Add((10, -1), 0)
        hbox3.Add(self.ttext, 0)
        hbox3.Add((10, -1), 0)
        hbox3.Add(self.calcbut, 0)
        hbox3.AddStretchSpacer()

        hbox4.Add((8,-1), 0)
        hbox4.Add(st4, 0)
        hbox4.Add(self.text_vsun, 0)
        hbox4.Add((10, -1), 0)
        hbox4.Add(st5, 0)
        hbox4.Add(self.text_vorb, 0)
        hbox4.Add((10, -1), 0)
        hbox4.Add(st6, 0)
        hbox4.Add(self.text_vlsr, 0)
        hbox4.Add((10, -1), 0)
        hbox4.Add(st7, 0)
        hbox4.Add(self.text_zrs, 0)
        hbox4.AddStretchSpacer()
        hbox4.Add(self.version, 0)

        hbox5.AddStretchSpacer()
        hbox5.Add(self.version, 0)
        hbox5.Add((10, -1), 0)

        vbox1.Add((-1, 20))
        vbox1.Add(hbox1, flag=wx.EXPAND|wx.RIGHT|wx.LEFT)
        #vbox1.Add((-1, 10))
        vbox1.Add(hbox1A, flag=wx.EXPAND|wx.RIGHT|wx.LEFT)
        vbox1.Add((-1, 10))
        vbox1.Add(hbox2, flag=wx.EXPAND|wx.RIGHT|wx.LEFT)
        vbox1.Add((-1, 10))
        vbox1.Add(hbox2A, flag=wx.EXPAND|wx.RIGHT|wx.LEFT)
        vbox1.Add((-1, 10))
        vbox1.Add(hbox3, flag=wx.ALIGN_LEFT)
        vbox1.Add((-1, 30))
        vbox1.Add(hbox4, flag=wx.ALIGN_LEFT)
        vbox1.Add((-1, 10))
        vbox1.Add(hbox5, flag=wx.ALIGN_RIGHT)


        self.radc = None
        self.SetSizer(vbox1)

    def calculate(self, evt):
        self.find_vlsr()

    def manage_date(self, evt):
        self.make_dtup()

    def manage_time(self, evt):
        self.make_dtup()

    def make_dtup(self):
        day = string.split(self.tc1.GetValue(), '/')
        tim = string.split(self.tc2.GetValue(), ':')
        lt = len(tim)
        if lt == 3:
           self.dtup = (int(day[0]),int(day[1]),int(day[2]),int(tim[0]),int(tim[1]),int(tim[2]))
        elif lt == 2:
           self.dtup = (int(day[0]),int(day[1]),int(day[2]),int(tim[0]),int(tim[1]),0)
        else:
           self.dtup = (int(day[0]),int(day[1]),int(day[2]),int(tim[0]),0,0)
        if self.now_cb.IsChecked():
            self.epd = ep.Date(ep.now())
        else:
            self.epd = ep.Date(self.dtup)
        llbl = '('+str(ep.localtime(self.epd))+' Local)'
        llbl = llbl.replace('-', '/')
        self.st1b.SetLabel(llbl)
        self.get_sunlong()
        self.tc3.ChangeValue("%5.1f deg" % self.sunlong)

    def use_current(self, evt):
        self.make_dtup()

    def get_sunlong(self):
        s = ep.Sun(self.epd)
        se = ep.Ecliptic(s)
        try:
            self.sunlong = math.degrees(float(se.lon))
        except AttributeError:
            self.sunlong = math.degrees(float(se.long))

    def getTargType(self,evt):
        c = self.set_tt.GetSelection()
        if c < 4: return
        self.make_dtup()
        self.scope.date = self.epd
        name = self.tts[c]
        line = self.tndict.get(name)
        self.targ_name = name
        self.targ_line = line
        pcs = line.split(':')
        if pcs[0] != '#':
            body = ep.readdb(line)
            body.compute(self.scope)
            # body.ra is an angle in radians
            #print (name+' AZEL '+str(body.az)+', '+str(body.alt))
            self.radc = (angle2tuple(body.ra), angle2tuple(body.dec))
            #print(name+" radc "),
            #print self.radc
        elif name == 'Sun':
            self.tmp_line = '#:Sun'
            sun = ep.Sun(self.scope)
            #print (name+' AZEL '+str(sun.az)+', '+str(sun.alt))
            #print (name+' (RA, DEC) = '+str(sun.ra)+', '+str(sun.dec))
            self.radc = (angle2tuple(sun.ra), angle2tuple(sun.dec))
            #print(name+" radc "),
            #print self.radc
        elif name == 'Jupiter':
            self.tmp_line = '#:Jupiter'
            j = ep.Jupiter(self.scope)
            #print (name+' AZEL '+str(j.az)+', '+str(j.alt))
            self.radc = (angle2tuple(j.ra), angle2tuple(j.dec))
            #print(name+" radc "),
            #print self.radc
        elif name == 'Moon':
            self.tmp_line = '#:Moon'
            m = ep.Moon(self.scope)
            #print (name+' AZEL '+str(m.az)+', '+str(m.alt))
            self.radc = (angle2tuple(m.ra), angle2tuple(m.dec))
            #print(name+" radc "),
            #print self.radc
        elif name == 'Mars':
            self.targ_line = '#:Mars'
            m = ep.Mars(self.scope)
            #print (name+' AZEL '+str(m.az)+', '+str(m.alt))
            self.radc = (angle2tuple(m.ra), angle2tuple(m.dec))
            #print(name+" radc "),
            #print self.radc
        elif name == 'Stow':
            self.targ_line = '#:Stow'
            plc = sky_pt(sky_pt.HADC,(0,0,0),(0,0,0),epd=self.epd)
            self.radc = plc.getLoc(sky_pt.RADC)
            #print(name+" radc "),
            #print self.radc
        else:
            self.ttext.SetValue('Unknown target!')
            return
        if self.radc is None:
            self.text_radc.ChangeValue('Can\'t find radc for '+line)
            return
        rah = tup2deg(self.radc[0])
        rad = 15.0*rah
        dec = tup2deg(self.radc[1])
        self.text_radc.ChangeValue("(%5.2f hr or %5.1f deg, %5.1f deg)" % (rah, rad, dec))
        plc = sky_pt(sky_pt.RADC, self.radc[0], self.radc[1], epd=self.epd)
        self.translate(plc)

    def onTargEnter(self, evt):
        c = self.set_tt.GetSelection()
        if c > 3: return
        ttxt = self.ttext.GetValue()
        ttxt = ttxt.strip()
        if ttxt.startswith('(') and ttxt.endswith(')'):
            ttxt = ttxt[1:-1]
        try:
            (c1s, c2s) = ttxt.split(',')
            c1f = float(c1s)
            c2f = float(c2s)
            tup1 = deg2tup(c1f)
            tup2 = deg2tup(c2f)
        except:
            self.ttext.SetValue('Format Error')
            return
        self.make_dtup()
        self.scope.date = self.epd
        try:
            if c == 0:
                self.targ_name = 'HADC'
                self.targ_line = '#:HADC:'+str(tup1)+':'+str(tup2)
                plc = sky_pt(sky_pt.HADC,tup1,tup2,epd=self.epd)
            elif c == 1:
                self.targ_name = 'AZEL'
                self.targ_line = '#:AZEL:'+str(tup1)+':'+str(tup2)
                plc = sky_pt(sky_pt.AZEL,tup1,tup2,epd=self.epd)
            elif c == 2:
                self.targ_name = 'GALA'
                self.targ_line = '#:GALA:'+str(tup1)+':'+str(tup2)
                plc = sky_pt(sky_pt.GALACTIC,tup1,tup2,epd=self.epd)
            elif c == 3:
                self.targ_name = 'RADC'
                self.targ_line = '#:RADC:'+str(tup1)+':'+str(tup2)
                plc = sky_pt(sky_pt.RADC,tup1,tup2,epd=self.epd)
            else:
                self.ttext.SetValue('Unknown target!')
                return
        except:
            self.ttext.SetValue('sky-pt Error')
            return
        self.radc = plc.getLoc(sky_pt.RADC)
        rah = tup2deg(self.radc[0])
        rad = 15.0*rah
        dec = tup2deg(self.radc[1])
        self.text_radc.ChangeValue("(%5.2f hr or %5.1f deg, %5.1f deg)" % (rah, rad, dec))
        self.translate(plc)

    def translate(self, plc):
        tecc = plc.getLoc(sky_pt.ECLIPTIC)
        tlond = tup2deg(tecc[0])  # ecliptic lon of target
        tlatd = tup2deg(tecc[1])  # ecliptic lon of target
        self.text_ec_aim.ChangeValue("%5.1f, %5.1f" % (tlond, tlatd))
        hadc = plc.getLoc(sky_pt.HADC)
        had = tup2deg(hadc[0])
        dcd = tup2deg(hadc[1])
        self.text_ha_aim.ChangeValue("%5.1f, %5.1f" % (had, dcd))
        azel = plc.getLoc(sky_pt.AZEL)
        azd = tup2deg(azel[0])
        eld = tup2deg(azel[1])
        self.text_az_aim.ChangeValue("%5.1f, %5.1f" % (azd, eld))
        gala = plc.getLoc(sky_pt.GALACTIC)
        glond = tup2deg(gala[0])
        glatd = tup2deg(gala[1])
        self.text_ga_aim.ChangeValue("%5.1f, %5.1f" % (glond, glatd))
        self.get_sunlong()
        self.tc3.ChangeValue("%5.1f deg" % self.sunlong)


    def find_vlsr(self):
        # telescope longitude is -71.091 deg or -1.2408 radians
        # radc is a tuple containing a pair of tuples for target.
        # radc[0] is a (hr, min, sec) tuple
        # radc[1] is the dec (deg, min, sec) angle tuple
        # Sun velocity apex is at 18 hr, 30 deg; convert to x, y, z
        # geocentric celestial for dot product with source, multiply by speed
        #x0 = 20.0 * math.cos(18.0 * pi / 12.0) * math.cos(30.0 * pi / 180.0)
        #y0 = 20.0 * math.sin(18.0 * pi / 12.0) * math.cos(30.0 * pi / 180.0)
        #z0 = 20.0 * math.sin(30.0 * pi / 180.0)
        # Sun velocity direction wrt LSR  geocentric equatorial rectangular
        # coordinates is x0, y0, z0 where z axis is towards N pole, and
        # x axis is direction of vernel equinox
        x0 = 0.0
        y0 = -17.321
        z0 = 10.0
        if self.chat:
            print ("Target radc: ", self.radc)
        try:
            tg_ra_rad = math.radians(15.0*tup2deg(self.radc[0]))
            tg_dec_rad = math.radians(tup2deg(self.radc[1]))
        except:
            self.ttext.SetValue('Target radc error')
            return
        ctra = math.cos(tg_ra_rad)
        stra = math.sin(tg_ra_rad)
        ctdc = math.cos(tg_dec_rad)
        stdc = math.sin(tg_dec_rad)
        # dot product of target & apex vectors
        vsun = x0*ctra*ctdc + y0*stra*ctdc + z0*stdc
        self.text_vsun.ChangeValue("%5.2f km/s" % vsun)
        # get target in geocentric ecliptic system
        sps = sky_pt(sky_pt.RADC, self.radc[0], self.radc[1], epd=self.epd)
        tecc = sps.getLoc(sky_pt.ECLIPTIC)
        tlond = tup2deg(tecc[0])  # ecliptic lon of target
        tlatd = tup2deg(tecc[1])  # ecliptic lon of target
        self.text_ec_aim.ChangeValue("%5.1f, %5.1f" % (tlond, tlatd))
        tlon = math.radians(tlond)
        tlat = math.radians(tlatd)
        self.get_sunlong()
        self.tc3.ChangeValue("%5.1f deg" % self.sunlong)
        slong = math.radians(self.sunlong)
        vorb = 30.0*math.cos(tlat)*math.sin(slong-tlon)
        self.text_vorb.ChangeValue("%5.2f km/s" % vorb)
        if self.chat:
            print("Target: cos(alpha)=%6.4f, sin(alpha)=%6.4f, dec=%6.3f (radians)," % (ctra, stra, tg_dec_rad))
            print("Radial velocity components: vsun=%5.2f and vorb=%5.2f (km/s)" % (vsun, vorb))
            print("Ecliptic: slong=%6.3f, tlon=%6.3f and tlat=%6.3f (radians)" % (slong, tlon, tlat))
            print("vsun > 0 and vorb > 0 each give a blue shift;"),
            print(" vlsr is -(vsun+vorb).")
        vlsr = -(vsun + vorb)
        self.text_vlsr.ChangeValue("%5.2f km/s" % vlsr)
        zrs = 1420.4 * (1.0 + vlsr/3.0e5)
        self.text_zrs.ChangeValue("%5.2f MHz" % zrs)



# end of class CtrlPanel

class sky_pt:
    RADC, GALACTIC, AZEL, HADC, ECLIPTIC, BODY = range(6)
    # Lat is 42.361, co-lat is 47.639 or 47:38:20.40
    TELESCOPE_LATITUDE = ep.degrees("42:21:38.67")
    TELESCOPE_LONGITUDE = ep.degrees("-71:05:27.84")

    def __init__(self, unit, locA, locB, epd=None):
        if unit != sky_pt.BODY:
            if len(locA) != 3 or len(locB) != 3:
                print("Bad Locations given")
                return
        else:
            name = locA
            sname = locB

        global os_name
        self.telescope = ep.Observer()
        self.telescope.lat = self.TELESCOPE_LATITUDE
        self.telescope.long = self.TELESCOPE_LONGITUDE
        self.telescope.pressure = 0
        self.telescope.elevation = 30
        self.location = None
        if epd == None:
            self.telescope.date = ep.now()
        else:
            self.telescope.date = epd
        #example: epd = ep.Date('2013/3/29 12:58:49')  this is UTC
        if unit == sky_pt.RADC:
            line = ('thing,f,' + loc2str(locA) + ','
                    + loc2str(locB) + ',1')
            self.location = ep.readdb(line)
        elif unit == sky_pt.GALACTIC:
            ga = ep.Galactic(loc2str(locA), loc2str(locB),
                             epoch=ep.J2000)
            eq = ep.Equatorial(ga)
            line = 'thing,f,' + str(eq.ra) + ',' + str(eq.dec) + ',1'
            self.location = ep.readdb(line)
        elif unit == sky_pt.AZEL:
            ra,dec = self.telescope.radec_of(loc2str(locA),
                                             loc2str(locB))
            line = 'thing,f,' + str(ra) + ',' + str(dec) + ',1'
            self.location = ep.readdb(line)
        elif unit == sky_pt.HADC:
            ra = ep.hours(self.telescope.sidereal_time()
                          - ep.degrees(loc2str(locA)))
            line = 'thing,f,' + str(ra) + ',' + loc2str(locB) + ',1'
            self.location = ep.readdb(line)
        elif unit == sky_pt.BODY:
            if name == 'Sun':
                bd = ep.Sun()
                self.location = bd
            else:
                print('Error, Unknown Body')
                return
        else:
            print('Error, Unknown Units')
            return
        self.location.compute(self.telescope)

    def getLoc(self, unit = RADC):
        self.location.compute(self.telescope)
        if unit == sky_pt.RADC:
            return (angle2tuple(self.location.ra),
                    angle2tuple(self.location.dec))
        elif unit == sky_pt.GALACTIC:
            ga = ep.Galactic(self.location)
            '''
            if os_name.find("Dar") != -1:       # OS-X
                return (angle2tuple(ga.lon), angle2tuple(ga.lat))
            else:
                return (angle2tuple(ga.long), angle2tuple(ga.lat))
            '''
            try:
                return (angle2tuple(ga.lon), angle2tuple(ga.lat))
            except AttributeError:
                return (angle2tuple(ga.long), angle2tuple(ga.lat))
        elif unit == sky_pt.AZEL:
            return (angle2tuple(self.location.az),
                    angle2tuple(self.location.alt))
        elif unit == sky_pt.HADC:
            ha = ep.degrees(self.telescope.sidereal_time() - self.location.ra)
            return (angle2tuple(ha), angle2tuple(self.location.dec))
        elif unit == sky_pt.ECLIPTIC:
            el = ep.Ecliptic(self.location)
            try:
                return (angle2tuple(el.lon), angle2tuple(el.lat))
            except AttributeError:
                return (angle2tuple(el.long), angle2tuple(el.lat))

#end of class sky_pt

# putting these here makes them a global for all classes

def loc2str(loc):
   return str(loc[0]) + ':' + str(loc[1]) + ':' + str(loc[2])

def angle2tuple(angle):
    x = str(angle).split(':')
    return (int(x[0]), int(x[1]), int(float(x[2])))

def deg2tup(arg):
    #if isinstance(arg, basestring):
    #    arg = float(arg)
    tmp1 = math.modf(arg)
    tmp2 = math.modf(60.0*tmp1[0])
    tmp3 = math.modf(60.0*tmp2[0])
    if arg < 0:
        tup = (int(tmp1[1]), -int(tmp2[1]), -int(tmp3[1]))
    else:
        tup = (int(tmp1[1]), int(tmp2[1]), int(tmp3[1]))
    return(tup)

def tup2deg(arg):
    deg = float(arg[0])
    dec = float(arg[1])/60.0 + float(arg[2])/3600.0
    if deg < 0.0:
        deg -= dec
    else:
        deg += dec
    return deg

def angle2deg(angle):
    x = str(angle).split(':')
    fp = float(x[1])/60.0 + float(x[2])/3600.0
    deg = float(x[0])
    if deg < 0.0:
        return deg - fp
    else:
        return deg + fp

def represents_tuple(s):
    try: return type(ast.literal_eval(s)) == tuple
    except SyntaxError: return False
    except ValueError: return False


if __name__ == '__main__':
    app = wx.App(0)
    MainFrame(None, title='Calculate VLSR for Junior Lab Telescopes')
    app.MainLoop()
