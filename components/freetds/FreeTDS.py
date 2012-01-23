"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The FreeTDS component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os
import os.path

class FreeTDS(Component):

	def __init__(self, config):
		super(FreeTDS, self).__init__('FreeTDS', os.path.dirname(__file__), config)

		self.download_url = 'ftp://ftp.ibiblio.org/pub/Linux/ALPHA/freetds/stable/freetds-%s.tar.gz' % self.version
		self.dependencies = [
			Dependency('OpenSSL', configureFlags=["--with-openssl=${COMPONENT_PATH}"]),
			Dependency('Ncurses', configureFlags=["--with-ncurses=${COMPONENT_PATH}"])
		]

	def configureFlags(self):
		flags = super(FreeTDS, self).configureFlags()

		flags.extend([
			'--enable-shared',
			'--disable-odbc'
		])

		return  flags
