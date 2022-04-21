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

import time, os, subprocess, sys
from openplotterSettings import language
from openplotterSignalkInstaller import connections

class Start(): 
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-maiana',currentLanguage)
		
		self.initialMessage = ''

		#TODO run read from here

	def start(self): 
		green = '' 
		black = '' 
		red = '' 

		return {'green': green,'black': black,'red': red}

class Check():
	def __init__(self, conf, currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-maiana',currentLanguage)
		
		self.initialMessage = _('Checking MAIANA transponder...')

	def check(self):
		green = '' 
		black = '' 
		red = '' 

		#TODO check localhost 10110 and "Suppress nmea0183 event" in sk connection
		
		#device
		device = self.conf.get('MAIANA', 'device')
		if not device:
			msg = _('There is no MAIANA device defined')
			if not red: red = msg
			else: red+= '\n    '+msg
		else:
			msg = _('MAIANA device')+': '+device
			if not green: green = msg
			else: green+= ' | '+msg

		#access
		skConnections = connections.Connections('MAIANA')
		result = skConnections.checkConnection()
		if result[0] == 'pending' or result[0] == 'error' or result[0] == 'repeat' or result[0] == 'permissions':
			if not red: red = result[1]
			else: red+= '\n    '+result[1]
		if result[0] == 'approved' or result[0] == 'validated':
			msg = _('Access to Signal K server validated')
			if not green: green = msg
			else: green+= ' | '+msg

		#service
		if device and (result[0] == 'approved' or result[0] == 'validated'):
			try:
				subprocess.check_output(['systemctl', 'is-active', 'openplotter-maiana-read']).decode(sys.stdin.encoding)
				msg = _('OpenPlotter MAIANA service is running')
				if not green: green = msg
				else: green+= ' | '+msg
			except:			
				msg = _('OpenPlotter MAIANA service is not running')
				if not red: red = msg
				else: red+= '\n    '+msg
		else:
			try:
				subprocess.check_output(['systemctl', 'is-active', 'openplotter-maiana-read']).decode(sys.stdin.encoding)
				msg = _('OpenPlotter MAIANA service is running')
				if not red: red = msg
				else: red+= '\n    '+msg
			except:			
				msg = _('OpenPlotter MAIANA service is not running')
				if not green: green = msg
				else: green+= ' | '+msg

		return {'green': green,'black': black,'red': red}

