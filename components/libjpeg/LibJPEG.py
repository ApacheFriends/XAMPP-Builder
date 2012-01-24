"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The LibJPEG component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os
import os.path

class LibJPEG(Component):

	def __init__(self, config):
		super(LibJPEG, self).__init__('LibJPEG', os.path.dirname(__file__), config)

		self.download_url = 'http://switch.dl.sourceforge.net/sourceforge/libjpeg/jpegsrc.v%s.tar.gz' % self.version
		
		self.buildSteps.insert(self.buildSteps.index('install'), self.createCommonDirectories)
		
		self.patches = [
			'libtool135update.zip'
		]
		
	def configureFlags(self):
		flags = super(LibJPEG, self).configureFlags()

		flags.extend([
			'--enable-shared'
		])
		
		return flags

	def installFlags(self):
		return [
			"install",
			"prefix=${DEST_DIR}${PREFIX}"
		]
		
	def createCommonDirectories(self, component, archs, builder):
		dirs = [
			'bin',
			'lib',
			'include',
			'man/man1'
		]
		
		for d in dirs:
			dir = self.buildPath + os.path.join(self.config.prefixPath, d)
			if not os.path.isdir(dir):
				path = os.makedirs(dir)

