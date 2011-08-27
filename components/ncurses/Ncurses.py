"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Ncurses component.
"""

from utils.Component import Component

import os.path

class Ncurses(Component):

    def __init__(self, config):
        super(Ncurses, self).__init__('Ncurses', os.path.dirname(__file__), config)

        self.download_url = 'http://ftp.gnu.org/pub/gnu/ncurses/ncurses-%s.tar.gz' % self.version

    def configureFlags(self):
        flags = super(Ncurses, self).configureFlags()

        flags.extend([
            '--with-shared'
        ])

        return  flags