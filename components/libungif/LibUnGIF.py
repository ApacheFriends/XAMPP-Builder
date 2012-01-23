"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The LibXML component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os
import os.path

class LibUnGIF(Component):

	def __init__(self, config):
		super(LibUnGIF, self).__init__('LibUnGIF', os.path.dirname(__file__), config)

		self.download_url = 'http://downloads.sourceforge.net/giflib/libungif-%s.tar.gz' % self.version

