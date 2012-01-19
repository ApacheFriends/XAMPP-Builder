"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The LibPNG component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class LibPNG(Component):

	def __init__(self, config):
		super(LibPNG, self).__init__('LibPNG', os.path.dirname(__file__), config)

		self.download_url = 'http://switch.dl.sourceforge.net/sourceforge/libpng/libpng-%s.tar.bz2' % self.version

		self.dependencies = [
			Dependency('ZLib', configureFlags=["--with-zlib-prefix=${COMPONENT_PATH}"]),
		]

