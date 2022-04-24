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

import os, subprocess, serial
from openplotterSettings import language

class Actions:
	def __init__(self,conf,currentLanguage):
		self.conf = conf
		currentdir = os.path.dirname(os.path.abspath(__file__))
		language.Language(currentdir,'openplotter-maiana',currentLanguage)
		if self.conf.get('GENERAL', 'debug') == 'yes': self.debug = True
		else: self.debug = False
		self.available = []
		self.available.append({'ID':'txOn','name':_('Turn MAIANA TX on'),"module": "openplotterMaiana",'data':False,'default':'','help':''})
		self.available.append({'ID':'txOff','name':_('Turn MAIANA TX off'),"module": "openplotterMaiana",'data':False,'default':'','help':''})

	def run(self,action,data):
		try:
			device = self.conf.get('MAIANA', 'device')
			ser = serial.Serial(device, 38400)
			if action == 'txOn': ser.write('tx on\r\n'.encode("utf-8"))
			elif action == 'txOff': ser.write('tx off\r\n'.encode("utf-8"))
		except Exception as e: 
			if self.debug: print('Error processing openplotter-maiana actions: '+str(e))
