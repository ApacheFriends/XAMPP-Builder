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

class LibXML(Component):

	def __init__(self, config):
		super(LibXML, self).__init__('LibXML', os.path.dirname(__file__), config)

		self.download_url = 'ftp://xmlsoft.org/libxml2/libxml2-%s.tar.gz' % self.version
		self.includeDir = "libxml2"

