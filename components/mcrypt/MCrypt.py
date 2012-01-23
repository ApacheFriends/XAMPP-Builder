"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The MCrypt component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os
import os.path

class MCrypt(Component):

	def __init__(self, config):
		super(MCrypt, self).__init__('MCrypt', os.path.dirname(__file__), config)

		self.download_url = 'http://downloads.sourceforge.net/mcrypt/libmcrypt-%s.tar.gz' % self.version

