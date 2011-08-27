"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Expat component.
"""

from utils.Component import Component

import os.path

class Expat(Component):

    def __init__(self, config):
        super(Expat, self).__init__('Expat', os.path.dirname(__file__), config)

        self.download_url = 'http://switch.dl.sourceforge.net/sourceforge/expat/expat-%s.tar.gz' % self.version
