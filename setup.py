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

from setuptools import setup
from openplotterMaiana import version

setup (
	name = 'openplotterMaiana',
	version = version.version,
	description = 'OpenPlotter integration of the MAIANA open source AIS transponder',
	license = 'GPLv3',
	author="Sailoog",
	author_email='info@sailoog.com',
	url='https://github.com/openplotter/openplotter-maiana',
	packages=['openplotterMaiana'],
	classifiers = ['Natural Language :: English',
	'Operating System :: POSIX :: Linux',
	'Programming Language :: Python :: 3'],
	include_package_data=True,
	entry_points={'console_scripts': ['openplotter-maiana=openplotterMaiana.openplotterMaiana:main','maianaPostInstall=openplotterMaiana.maianaPostInstall:main','maianaPreUninstall=openplotterMaiana.maianaPreUninstall:main','openplotter-maiana-read=openplotterMaiana.openplotterMaianaRead:main']},
	data_files=[('share/applications', ['openplotterMaiana/data/openplotter-maiana.desktop']),('share/pixmaps', ['openplotterMaiana/data/openplotter-maiana.png']),],
	)
