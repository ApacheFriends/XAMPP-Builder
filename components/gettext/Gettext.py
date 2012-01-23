"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

  The Gettext component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os
import os.path

class Gettext(Component):

	def __init__(self, config):
		super(Gettext, self).__init__('Gettext', os.path.dirname(__file__), config)

		self.download_url = 'http://ftp.gnu.org/pub/gnu/gettext/gettext-%s.tar.gz' % self.version

	def configureFlags(self):
		flags = super(Gettext, self).configureFlags()

		flags.extend([
			'--disable-java',
			'--disable-native-java',
			'--enable-relocatable',
			'--without-man',
			'--without-emacs'
		])

		return  flags
