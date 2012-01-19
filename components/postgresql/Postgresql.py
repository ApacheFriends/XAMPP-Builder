"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The Postgresql component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class Postgresql(Component):

	def __init__(self, config):
		super(Postgresql, self).__init__('Postgresql', os.path.dirname(__file__), config)

		self.download_url = 'http://ftp8.de.postgresql.org/pub/misc/pgsql/latest/postgresql-%s.tar.bz2' % self.version
		self.supportsOnPassUniversalBuild = False