"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The FreeType component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class FreeType(Component):

	def __init__(self, config):
		super(FreeType, self).__init__('FreeType', os.path.dirname(__file__), config)

		self.download_url = 'http://download.savannah.gnu.org/releases/freetype/freetype-%s.tar.gz' % self.version
