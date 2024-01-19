#!/usr/bin/env python3

# This file is part of OpenPlotter.
# Copyright (C) 2022 by Sailoog <https://github.com/openplotter/openplotter-maiana>
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

import time, os, subprocess, sys, ujson
from openplotterSettings import language
from openplotterSettings import platform
from openplotterSignalkInstaller import connections

class Start(): 
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-maiana',currentLanguage)
		
		self.initialMessage = _('Starting MAIANA transponder...')

	def start(self): 
		green = '' 
		black = '' 
		red = '' 

		subprocess.call(['pkill', '-f', 'openplotter-maiana-read'])
		subprocess.Popen('openplotter-maiana-read')
		time.sleep(1)

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		self.platform = platform.Platform()
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-maiana',currentLanguage)
		
		self.initialMessage = _('Checking MAIANA transponder...')

	def check(self):
		green = '' 
		black = '' 
		red = '' 
		
		#device
		device = self.conf.get('MAIANA', 'device')
		if not device:
			msg = _('There is no MAIANA device defined')
			if not red: red = msg
			else: red+= '\n    '+msg
		else:
			msg = _('MAIANA device')+': '+device
			if not black: black = msg
			else: black+= ' | '+msg

		#check device and server settings
		try:
			setting_file = self.platform.skDir+'/settings.json'
			with open(setting_file) as data_file:
				data = ujson.load(data_file)
		except: data = {}
		if 'pipedProviders' in data: data2 = data['pipedProviders']
		else: data2 = []

		#check maianaCommand connection
		commands = False
		for i in data2:
			if i['id'] == 'maianaCommand':
				commands = True
				errors = False
				try:
					if not i['enabled']: errors = True
					if i['pipeElements'][0]['options']['type'] != "NMEA0183": errors = True
					if i['pipeElements'][0]['options']['subOptions']['type'] != "udp": errors = True
					if i['pipeElements'][0]['options']['subOptions']['port'] != "40440": errors = True
					if i['pipeElements'][0]['options']['subOptions']['sentenceEvent'] != "maianaCommand": errors = True
				except: errors = True
				if errors:
					msg = _('Signal K connection "maianaCommand" has errors. Reinstall "MAIANA AIS transponder" app.')
					if not red: red = msg
					else: red+= '\n    '+msg
				else:
					msg = _('maianaCommand connection OK')
					if not black: black = msg
					else: black+= ' | '+msg
		if not commands:
			msg = _('Signal K connection "maianaCommand" does not exists. Reinstall "MAIANA AIS transponder" app.')
			if not red: red = msg
			else: red+= '\n    '+msg

		##check maiana connection
		if device:
			deviceOK = False
			errors = False
			for i in data2:
				try:
					if device in i['pipeElements'][0]['options']['subOptions']['device']:
						deviceOK = True
						if not i['enabled']: errors = True
						if i['pipeElements'][0]['options']['subOptions']['type'] != "serial": errors = True
						if i['pipeElements'][0]['options']['subOptions']['baudrate'] != 38400: errors = True
						if i['pipeElements'][0]['options']['type'] != 'NMEA0183': errors = True
						if 'suppress0183event' in i['pipeElements'][0]['options']['subOptions']:
							if not i['pipeElements'][0]['options']['subOptions']['suppress0183event']: errors = True
						if 'toStdout' in i['pipeElements'][0]['options']['subOptions']:
							if not "maianaCommand" in i['pipeElements'][0]['options']['subOptions']['toStdout']: errors = True
						else: errors = True
				except: pass
				if errors:
					msg = _('MAIANA Signal K connection has errors. Please try again.')
					self.conf.set('MAIANA', 'device', '')
					if not red: red = msg
					else: red+= '\n    '+msg
				else:
					msg = _('MAIANA connection OK')
					if not black: black = msg
					else: black+= ' | '+msg
			if not deviceOK:
				msg = _('MAIANA Signal K connection does not exists.')
				if not red: red = msg
				else: red+= '\n    '+msg

		#check NMEA 0183 over TCP (10110) interface
		nmeaOK = True
		if 'interfaces' in data: data2 = data['interfaces']
		else: data2 = []
		if 'nmea-tcp' in data2:
			if not data2['nmea-tcp']: nmeaOK = False
		if not nmeaOK:
			msg = _('NMEA 0183 over TCP (10110) interface is disabled. Check Signal K server settings')
			if not red: red = msg
			else: red+= '\n    '+msg
		else:
			msg = _('NMEA 0183 over TCP (10110) interface OK')
			if not black: black = msg
			else: black+= ' | '+msg

		#access
		skConnections = connections.Connections('MAIANA')
		result = skConnections.checkConnection()
		if result[0] == 'pending' or result[0] == 'error' or result[0] == 'repeat' or result[0] == 'permissions':
			if not red: red = result[1]
			else: red+= '\n    '+result[1]
		if result[0] == 'approved' or result[0] == 'validated':
			msg = _('Access to Signal K server validated')
			if not black: black = msg
			else: black+= ' | '+msg

		# check service
		test = subprocess.check_output(['ps','aux']).decode(sys.stdin.encoding)
		if device and (result[0] == 'approved' or result[0] == 'validated'):
			if 'openplotter-maiana-read' in test: 
				msg = _('running')
				if not green: green = msg
				else: green+= ' | '+msg
			else:
				msg = _('not running')
				if red: red += '\n   '+msg
				else: red = msg
		else:
			if 'openplotter-maiana-read' in test: 
				msg = _('running')
				if red: red += '\n   '+msg
				else: red = msg
			else:
				msg = _('not running')
				if not black: black = msg
				else: black+= ' | '+msg

		return {'green': green,'black': black,'red': red}

