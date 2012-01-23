"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The LibXSLT component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class LibXSLT(Component):

	def __init__(self, config):
		super(LibXSLT, self).__init__('LibXSLT', os.path.dirname(__file__), config)

		self.download_url = 'ftp://xmlsoft.org/libxslt/libxslt-%s.tar.gz' % self.version
		self.dependencies = [
			Dependency('LibXML', configureFlags=["--with-libxml-prefix=${COMPONENT_PATH}", "--with-libxml-include-prefix=${INCLUDE_PATH}", "--with-libxml-libs-prefix=${LIB_PATH}"])
		]
