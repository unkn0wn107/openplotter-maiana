#!/usr/bin/env python3

# This file is part of Openplotter.
# Copyright (C) 2021 by Sailoog <https://github.com/openplotter/openplotter-maiana>
#
# Openplotter is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# any later version.
# Openplotter is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Openplotter. If not, see <http://www.gnu.org/licenses/>.

import wx, os, webbrowser, subprocess, time, ujson, serial, requests, re
import wx.richtext as rt
from openplotterSettings import conf
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSignalkInstaller import connections
from .version import version

class MyFrame(wx.Frame):
	def __init__(self):
		self.conf = conf.Conf()
		self.conf_folder = self.conf.conf_folder
		self.platform = platform.Platform()
		self.currentdir = os.path.dirname(os.path.abspath(__file__))
		self.currentLanguage = self.conf.get('GENERAL', 'lang')
		self.language = language.Language(self.currentdir,'openplotter-maiana',self.currentLanguage)

		wx.Frame.__init__(self, None, title=_('MAIANA AIS transponder')+' '+version, size=(800,444))
		self.SetFont(wx.Font(10, wx.FONTFAMILY_DEFAULT, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_NORMAL))
		icon = wx.Icon(self.currentdir+"/data/openplotter-maiana.png", wx.BITMAP_TYPE_PNG)
		self.SetIcon(icon)
		self.CreateStatusBar()
		font_statusBar = self.GetStatusBar().GetFont()
		font_statusBar.SetWeight(wx.BOLD)
		self.GetStatusBar().SetFont(font_statusBar)

		self.toolbar1 = wx.ToolBar(self, style=wx.TB_TEXT)
		toolHelp = self.toolbar1.AddTool(101, _('Help'), wx.Bitmap(self.currentdir+"/data/help.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolHelp, toolHelp)
		if not self.platform.isInstalled('openplotter-doc'): self.toolbar1.EnableTool(101,False)
		toolSettings = self.toolbar1.AddTool(102, _('Settings'), wx.Bitmap(self.currentdir+"/data/settings.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSettings, toolSettings)
		self.toolbar1.AddSeparator()
		aproveSK = self.toolbar1.AddTool(105, _('Approve'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onAproveSK, aproveSK)
		connectionSK = self.toolbar1.AddTool(106, _('Allowed'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onConnectionSK, connectionSK)
		self.toolbar1.AddSeparator()
		self.connInit = _('MAIANA Signal K connection')
		self.SKconn = wx.ComboBox(self.toolbar1, 103, self.connInit, choices=[], size=(250,-1), style=wx.CB_DROPDOWN)
		toolSKconn = self.toolbar1.AddControl(self.SKconn)
		self.Bind(wx.EVT_COMBOBOX, self.onSKconn, toolSKconn)
		showSK = self.toolbar1.AddTool(104, _('Connections'), wx.Bitmap(self.currentdir+"/data/sk.png"))
		self.Bind(wx.EVT_TOOL, self.onShowSK, showSK)

		self.notebook = wx.Notebook(self)
		self.notebook.Bind(wx.EVT_NOTEBOOK_PAGE_CHANGED, self.onTabChange)
		self.settings = wx.Panel(self.notebook)
		self.firmware = wx.Panel(self.notebook)
		self.notebook.AddPage(self.settings, _('Settings'))
		self.notebook.AddPage(self.firmware, _('Firmware'))
		self.il = wx.ImageList(24, 24)
		img0 = self.il.Add(wx.Bitmap(self.currentdir+"/data/settings2.png", wx.BITMAP_TYPE_PNG))
		img1 = self.il.Add(wx.Bitmap(self.currentdir+"/data/driver.png", wx.BITMAP_TYPE_PNG))
		self.notebook.AssignImageList(self.il)
		self.notebook.SetPageImage(0, img0)
		self.notebook.SetPageImage(1, img1)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar1, 0, wx.EXPAND)
		vbox.Add(self.notebook, 1, wx.EXPAND)
		self.SetSizer(vbox)

		self.pageSettings()
		self.pageFirmware()

		maxi = self.conf.get('GENERAL', 'maximize')
		if maxi == '1': self.Maximize()

		self.Centre()

		self.onRead()

	def ShowStatusBar(self, w_msg, colour):
		self.GetStatusBar().SetForegroundColour(colour)
		self.SetStatusText(w_msg)

	def ShowStatusBarRED(self, w_msg):
		self.ShowStatusBar(w_msg, (130,0,0))

	def ShowStatusBarGREEN(self, w_msg):
		self.ShowStatusBar(w_msg, (0,130,0))

	def ShowStatusBarBLACK(self, w_msg):
		self.ShowStatusBar(w_msg, wx.BLACK) 

	def ShowStatusBarYELLOW(self, w_msg):
		self.ShowStatusBar(w_msg,(255,140,0)) 

	def onTabChange(self, event):
		try:
			self.SetStatusText('')
		except:pass

	def OnToolHelp(self, event): 
		url = "/usr/share/openplotter-doc/external/maiana_app.html"
		webbrowser.open(url, new=2)

	def OnToolSettings(self, event=0): 
		subprocess.call(['pkill', '-f', 'openplotter-settings'])
		subprocess.Popen('openplotter-settings')

	def onAproveSK(self,e):
		if self.platform.skPort: 
			url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/security/access/requests'
			webbrowser.open(url, new=2)

	def onConnectionSK(self,e):
		if self.platform.skPort: 
			url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/security/devices'
			webbrowser.open(url, new=2)

	def onShowSK(self, event):
		if self.platform.skPort: 
			url = self.platform.http+'localhost:'+self.platform.skPort+'/admin/#/serverConfiguration/connections/-'
			webbrowser.open(url, new=2)

	def onRead(self):
		self.ShowStatusBarYELLOW(_('Reading MAIANA device settings...'))
		self.mmsi.SetValue('')
		self.vesselName.SetValue('')
		self.callSign.SetValue('')
		self.vesselType.SetValue('')
		self.LOA.SetValue('')
		self.beam.SetValue('')
		self.portOffset.SetValue('')
		self.bowOffset.SetValue('')
		self.logger.Clear()
		self.logger2.Clear()
		self.device = self.conf.get('MAIANA', 'device')
		if self.conf.get('MAIANA', 'noiseDetect') == '1': self.toolbar3.ToggleTool(304,True)
		else: self.toolbar3.ToggleTool(304,False)
		deviceOld = self.device
		availableIDs = []
		selected = ''
		self.tx = False
		try:
			setting_file = self.platform.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except: data = {}
		if 'pipedProviders' in data:
			data = data['pipedProviders']
		else: data = []
		for i in data:
			enabled = ''
			skID = ''
			dataType = ''
			device = ''
			baudrate = ''
			connectionType = ''
			try:
				enabled = i['enabled']
				skID = i['id']
				dataType = i['pipeElements'][0]['options']['type']
				dataSubOptions = i['pipeElements'][0]['options']['subOptions']
				device = dataSubOptions['device']
				baudrate = dataSubOptions['baudrate']
				connectionType = dataSubOptions['type']
				if enabled and connectionType == 'serial' and baudrate == 38400 and dataType == 'NMEA0183':
					availableIDs.append(skID)
					if device == self.device: selected = skID
			except: pass

		self.SKconn.Clear()
		self.SKconn.AppendItems(availableIDs)
		if selected: 
			self.SKconn.SetValue(selected)
		else:
			self.device = ''
			self.conf.set('MAIANA', 'device', self.device)
			self.SKconn.SetValue(self.connInit)
			self.toolbar3.EnableTool(302,False)
			self.toolbar3.EnableTool(303,False)
			self.ShowStatusBarRED(_('Select the Signal K connection for the MAIANA device'))

		if self.device:
			ser = serial.Serial(self.device, 38400)
			ser.write('sys?\r\n'.encode("utf-8"))
			ser.write('station?\r\n'.encode("utf-8"))
			ser.write('tx?\r\n'.encode("utf-8"))
			self.toolbar3.EnableTool(302,True)
			self.toolbar3.EnableTool(303,True)
			time.sleep(0.5)
			resp = requests.get(self.platform.http+'localhost:'+self.platform.skPort+'/signalk/v1/api/vessels/self/MAIANA/', verify=False)
			try:
				data = ujson.loads(resp.content)
			except: data = {}

			self.logger.BeginFontSize(10)
			self.logger.WriteText(_('Hardware revision'))
			if 'hardwareRevision' in data: self.logger.WriteText(': '+data['hardwareRevision']['value'])
			self.logger.Newline()
			self.logger.WriteText(_('Firmware revision'))
			if 'firmwareRevision' in data: self.logger.WriteText(': '+data['firmwareRevision']['value'])
			self.logger.Newline()
			self.logger.WriteText(_('Type of MCU'))
			if 'MCUtype' in data: self.logger.WriteText(': '+data['MCUtype']['value'])
			self.logger.Newline()
			self.logger.WriteText(_('Serial number'))
			if 'serialNumber' in data: self.logger.WriteText(': '+data['serialNumber']['value'])
			self.logger.Newline()
			
			self.logger2.BeginFontSize(10)
			self.logger2.WriteText(_('Transmitter hardware module'))
			if 'transmission' in data:
				if 'hardwarePresent' in data['transmission']:
					if data['transmission']['hardwarePresent']['value'] == 1: 
						self.logger2.BeginTextColour((0, 130, 0))
						self.logger2.WriteText(': '+_('present'))
					else: 
						self.logger2.BeginTextColour((130, 0, 0))
						self.logger2.WriteText(': '+_('not present'))
			self.logger2.EndTextColour()
			self.logger2.Newline()
			self.logger2.WriteText(_('Hardware TX switch'))
			if 'transmission' in data:
				if 'hardwareSwitch' in data['transmission']:
					if data['transmission']['hardwareSwitch']['value'] == 1: 
						self.logger2.BeginTextColour((0, 130, 0))
						self.logger2.WriteText(': '+_('ON'))
					else: 
						self.logger2.BeginTextColour((130, 0, 0))
						self.logger2.WriteText(': '+_('OFF'))
			self.logger2.EndTextColour()
			self.logger2.Newline()
			self.logger2.WriteText(_('Software TX switch'))
			if 'transmission' in data:
				if 'softwareSwitch' in data['transmission']:
					if data['transmission']['softwareSwitch']['value'] == 1: 
						self.logger2.BeginTextColour((0, 130, 0))
						self.tx = True
						self.logger2.WriteText(': '+_('ON'))
						self.toolbar3.SetToolNormalBitmap(302,wx.Bitmap(self.currentdir+"/data/switch-on.png"))
					else:
						self.tx = False
						self.logger2.BeginTextColour((130, 0, 0))
						self.logger2.WriteText(': '+_('OFF'))
						self.toolbar3.SetToolNormalBitmap(302,wx.Bitmap(self.currentdir+"/data/switch-off.png"))
			self.logger2.EndTextColour()
			self.logger2.Newline()
			self.logger2.WriteText(_('Station data'))
			if 'transmission' in data:
				if 'stationData' in data['transmission']:
					if data['transmission']['stationData']['value'] == 1: 
						self.logger2.BeginTextColour((0, 130, 0))
						self.logger2.WriteText(': '+_('provided'))
					else: 
						self.logger2.BeginTextColour((130, 0, 0))
						self.logger2.WriteText(': '+_('not provided'))
			self.logger2.EndTextColour()
			self.logger2.Newline()
			self.logger2.WriteText(_('Status'))
			if 'transmission' in data:
				if 'status' in data['transmission']:
					if data['transmission']['status']['value'] == 1:
						self.logger2.BeginTextColour((0, 130, 0))
						self.logger2.WriteText(': '+_('transmitting'))
					else:
						self.logger2.BeginTextColour((130, 0, 0))
						self.logger2.WriteText(': '+_('not transmitting'))
			self.logger2.EndTextColour()
			self.logger2.Newline()
			self.logger2.WriteText(_('Channel A latest transmitted message'))
			self.logger2.WriteText(': ')
			self.logger2.Newline()
			if 'channelA' in data:
				if 'transmittedMessageType' in data['channelA']:
					if data['channelA']['transmittedMessageType']['value']:
						self.logger2.WriteText('   '+_('Type'))
						self.logger2.WriteText(': '+data['channelA']['transmittedMessageType']['value'])
						self.logger2.Newline()

						self.logger2.WriteText('   '+_('Time'))
						self.logger2.WriteText(': '+data['channelA']['transmittedMessageType']['timestamp'])
						self.logger2.Newline()
			self.logger2.WriteText(_('Channel B latest transmitted message'))
			self.logger2.WriteText(': ')
			self.logger2.Newline()
			if 'channelB' in data:
				if 'transmittedMessageType' in data['channelB']:
					if data['channelB']['transmittedMessageType']['value']:
						self.logger2.WriteText('   '+_('Type'))
						self.logger2.WriteText(': '+data['channelB']['transmittedMessageType']['value'])
						self.logger2.Newline()
						self.logger2.WriteText('   '+_('Time'))
						self.logger2.WriteText(': '+data['channelB']['transmittedMessageType']['timestamp'])
						self.logger2.Newline()
			self.logger2.WriteText(_('Channel A noise floor'))
			self.logger2.WriteText(': ')
			if 'channelA' in data:
				if 'noiseFloor' in data['channelA']: self.logger2.WriteText(str(data['channelA']['noiseFloor']['value']))
			self.logger2.Newline()
			self.logger2.WriteText(_('Channel B noise floor'))
			self.logger2.WriteText(': ')
			if 'channelB' in data:
				if 'noiseFloor' in data['channelB']: self.logger2.WriteText(str(data['channelB']['noiseFloor']['value']))

			if 'station' in data:
				if 'MMSI' in data['station']: self.mmsi.SetValue(data['station']['MMSI']['value'])
				if 'callSign' in data['station']: self.callSign.SetValue(data['station']['callSign']['value'])
				if 'vesselName' in data['station']: self.vesselName.SetValue(data['station']['vesselName']['value'])
				if 'vesselType' in data['station']:
					if data['station']['vesselType']['value'] == 30: self.vesselType.SetSelection(0)
					elif data['station']['vesselType']['value'] == 34: self.vesselType.SetSelection(1)
					elif data['station']['vesselType']['value'] == 36: self.vesselType.SetSelection(2)
					elif data['station']['vesselType']['value'] == 37: self.vesselType.SetSelection(3)
				if 'LOA' in data['station']: self.LOA.SetValue(str(data['station']['LOA']['value']))
				if 'beam' in data['station']: self.beam.SetValue(str(data['station']['beam']['value']))
				if 'bowOffset' in data['station']: self.bowOffset.SetValue(str(data['station']['bowOffset']['value']))
				if 'portOffset' in data['station']: self.portOffset.SetValue(str(data['station']['portOffset']['value']))

			self.ShowStatusBarGREEN(_('Done'))


		self.toolbar1.EnableTool(105,False)
		skConnections = connections.Connections('MAIANA')
		result = skConnections.checkConnection()
		if result[0] == 'pending':
			self.toolbar1.EnableTool(105,True)
			self.ShowStatusBarYELLOW(result[1]+_(' Press "Approve" and then "Refresh".'))
		elif result[0] == 'error':
			self.ShowStatusBarRED(result[1])
		elif result[0] == 'repeat':
			self.ShowStatusBarYELLOW(result[1]+_(' Press "Refresh".'))
		elif result[0] == 'permissions':
			self.ShowStatusBarYELLOW(result[1]+_(' Press "Allowed".'))
		elif result[0] == 'approved':
			self.ShowStatusBarGREEN(result[1])

		if deviceOld != self.device:
			if self.device:
				subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'openplotter-maiana-read', 'restart'])
			else:
				subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'openplotter-maiana-read', 'stop'])
		else:
			if self.device:
				try:
					subprocess.check_output(['systemctl', 'is-active', 'openplotter-maiana-read']).decode(sys.stdin.encoding)
				except:
					subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'openplotter-maiana-read', 'restart'])

	def onSKconn(self, event):
		deviceOld = self.conf.get('MAIANA', 'device')
		selectedID = self.SKconn.GetValue()
		try:
			setting_file = self.platform.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except: data = {}
		if 'pipedProviders' in data:
			data = data['pipedProviders']
		else: data = []
		for i in data:
			skID = ''
			device = ''
			try:
				skID = i['id']
				dataSubOptions = i['pipeElements'][0]['options']['subOptions']
				device = dataSubOptions['device']
				if selectedID == skID:
					self.device = device
					self.conf.set('MAIANA', 'device', self.device)
			except: pass
		if deviceOld != self.device:
			if self.device:
				subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'openplotter-maiana-read', 'restart'])
				time.sleep(1)
			else:
				subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'openplotter-maiana-read', 'stop'])
		else:
			if self.device:
				try:
					subprocess.check_output(['systemctl', 'is-active', 'openplotter-maiana-read']).decode(sys.stdin.encoding)
				except:
					subprocess.Popen([self.platform.admin, 'python3', self.currentdir+'/service.py', 'openplotter-maiana-read', 'restart'])
					time.sleep(1)
		self.onRead()

	def pageSettings(self):
		self.logger2 = rt.RichTextCtrl(self.settings, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger2.SetMargins((10,10))

		mmsiLabel = wx.StaticText(self.settings, label=_('MMSI'))
		self.mmsi = wx.TextCtrl(self.settings)
		vesselNameLabel = wx.StaticText(self.settings, label=_('Vessel name'))
		self.vesselName = wx.TextCtrl(self.settings)
		callSignLabel = wx.StaticText(self.settings, label=_('Call sign'))
		self.callSign = wx.TextCtrl(self.settings)
		vesselTypeLabel = wx.StaticText(self.settings, label=_('Vessel type'))
		self.vesselType = wx.ComboBox(self.settings, 701, choices=['Fishing','Diving','Sailing','Pleasure craft'], style=wx.CB_DROPDOWN)
		LOAlabel = wx.StaticText(self.settings, label=_('LOA'))
		self.LOA = wx.TextCtrl(self.settings)
		beamLabel = wx.StaticText(self.settings, label=_('Beam'))
		self.beam = wx.TextCtrl(self.settings)
		portOffsetLabel = wx.StaticText(self.settings, label=_('Port Offset'))
		self.portOffset = wx.TextCtrl(self.settings)
		bowOffsetLabel = wx.StaticText(self.settings, label=_('Bow Offset'))
		self.bowOffset = wx.TextCtrl(self.settings)
		unitsLabel = wx.StaticText(self.settings, label=_('Units: meters'))

		self.toolbar3 = wx.ToolBar(self.settings, style=wx.TB_TEXT)
		toolRefresh = self.toolbar3.AddTool(301, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolRefresh, toolRefresh)
		self.toolbar3.AddSeparator()
		toolTX = self.toolbar3.AddTool(302, _('Software TX switch'), wx.Bitmap(self.currentdir+"/data/switch-off.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolTX, toolTX)
		self.toolbar3.AddSeparator()
		toolNoise = self.toolbar3.AddCheckTool(304, _('Detect noise'), wx.Bitmap(self.currentdir+"/data/notifications.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolNoise, toolNoise)
		self.toolbar3.AddSeparator()
		toolSave = self.toolbar3.AddTool(303, _('Save station data'), wx.Bitmap(self.currentdir+"/data/apply.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolSave, toolSave)

		hbox1 = wx.BoxSizer(wx.VERTICAL)
		hbox1.Add(self.logger2, 1, wx.EXPAND, 0)

		hbox2 = wx.BoxSizer(wx.VERTICAL)
		hbox2.Add(mmsiLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(self.mmsi, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(vesselNameLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(self.vesselName, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(LOAlabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(self.LOA, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(portOffsetLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.Add(self.portOffset, 0, wx.ALL | wx.EXPAND, 2)
		hbox2.AddSpacer(10)
		hbox2.Add(unitsLabel, 0, wx.ALL | wx.EXPAND, 5)

		hbox3 = wx.BoxSizer(wx.VERTICAL)
		hbox3.Add(callSignLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(self.callSign, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(vesselTypeLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(self.vesselType, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(beamLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(self.beam, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(bowOffsetLabel, 0, wx.ALL | wx.EXPAND, 2)
		hbox3.Add(self.bowOffset, 0, wx.ALL | wx.EXPAND, 2)

		hbox4 = wx.BoxSizer(wx.HORIZONTAL)
		hbox4.Add(hbox1, 2, wx.ALL | wx.EXPAND, 5)
		hbox4.Add(hbox2, 1, wx.ALL | wx.EXPAND, 5)
		hbox4.Add(hbox3, 1, wx.ALL | wx.EXPAND, 5)

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar3, 0)
		vbox.Add(hbox4, 1, wx.ALL | wx.EXPAND, 0)
		self.settings.SetSizer(vbox)

	def OnToolNoise(self,e):
		if self.toolbar3.GetToolState(304):
			self.conf.set('MAIANA', 'noiseDetect', '1')
		else:
			self.conf.set('MAIANA', 'noiseDetect', '0')

	def OnToolSave(self, event):
		mmsi = self.mmsi.GetValue()
		if not re.match('^[0-9]{9,9}$', mmsi):
			self.ShowStatusBarRED(_('Invalid MMSI'))
			return

		vesselName = self.vesselName.GetValue()
		vesselName = vesselName.upper()
		if not re.match('^[0-9A-Z]{1,20}$', vesselName):
			self.ShowStatusBarRED(_('Invalid vessel name'))
			return

		callSign = self.callSign.GetValue()
		if not re.match('^[0-9A-Z]{0,7}$', callSign):
			self.ShowStatusBarRED(_('Invalid call sign'))
			return

		vesselType = self.vesselType.GetSelection()
		if vesselType == 0: vesselType = '30'
		elif vesselType == 1: vesselType = '34'
		elif vesselType == 2: vesselType = '36'
		elif vesselType == 3: vesselType = '37'
		else:
			self.ShowStatusBarRED(_('Invalid vessel type'))
			return

		try: LOA = int(self.LOA.GetValue())
		except:
			self.ShowStatusBarRED(_('Invalid LOA'))
			return

		try: beam = int(self.beam.GetValue())
		except:
			self.ShowStatusBarRED(_('Invalid Beam'))
			return
		
		try: bowOffset = float(self.bowOffset.GetValue())
		except:
			self.ShowStatusBarRED(_('Invalid bow offset'))
			return

		try: portOffset = float(self.portOffset.GetValue())
		except:
			self.ShowStatusBarRED(_('Invalid port offset'))
			return

		command = 'station '+str(mmsi)+','+str(vesselName)+','+str(callSign)+','+str(vesselType)+','+str(LOA)+','+str(beam)+','+str(portOffset)+','+str(bowOffset)+'\r\n'
		ser = serial.Serial(self.device, 38400)
		ser.write(command.encode("utf-8"))
		self.onRead()

	def OnToolTX(self, event):
		ser = serial.Serial(self.device, 38400)
		if self.tx: ser.write('tx off\r\n'.encode("utf-8"))
		else: ser.write('tx on\r\n'.encode("utf-8"))
		self.onRead()

	def OnToolRefresh(self, event):
		self.onRead()

	############################################################################

	def pageFirmware(self):
		self.toolbar2 = wx.ToolBar(self.firmware, style=wx.TB_TEXT)
		toolRefresh = self.toolbar2.AddTool(201, _('Refresh'), wx.Bitmap(self.currentdir+"/data/refresh.png"))
		self.Bind(wx.EVT_TOOL, self.OnToolRefresh, toolRefresh)

		self.logger = rt.RichTextCtrl(self.firmware, style=wx.TE_MULTILINE|wx.TE_READONLY|wx.TE_DONTWRAP|wx.LC_SORT_ASCENDING)
		self.logger.SetMargins((10,10))

		vbox = wx.BoxSizer(wx.VERTICAL)
		vbox.Add(self.toolbar2, 0, wx.EXPAND, 0)
		vbox.Add(self.logger, 1, wx.EXPAND, 0)

		self.firmware.SetSizer(vbox)

################################################################################

def main():
	try:
		platform2 = platform.Platform()
		if not platform2.postInstall(version,'maiana'):
			subprocess.Popen(['openplotterPostInstall', platform2.admin+' maianaPostInstall'])
			return
	except: pass

	app = wx.App()
	MyFrame().Show()
	time.sleep(1)
	app.MainLoop()

if __name__ == '__main__':
	main()
