"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The LibJPEG component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class LibJPEG(Component):

	def __init__(self, config):
		super(LibJPEG, self).__init__('LibJPEG', os.path.dirname(__file__), config)

		self.download_url = 'http://freshmeat.net/redir/libjpeg/5665/url_tgz/jpegsrc.v%s.tar.gz' % self.version

