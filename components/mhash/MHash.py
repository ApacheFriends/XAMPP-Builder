"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The MHash component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os
import os.path

class MHash(Component):

	def __init__(self, config):
		super(MHash, self).__init__('MHash', os.path.dirname(__file__), config)

		self.download_url = 'http://downloads.sourceforge.net/mhash/mhash-%s.tar.gz' % self.version

