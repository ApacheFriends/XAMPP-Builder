"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The LibLTDL component.
"""

from utils.Component import Component

import os.path

class LibLTDL(Component):

    def __init__(self, config):
        super(LibLTDL, self).__init__('LibLTDL', os.path.dirname(__file__), config)

        self.download_url = 'http://ftp.gnu.org/gnu/libtool/libtool-%s.tar.gz' % self.version

    def extraTarFlags(self):
        return [
            '--strip', '2',
            '--include', 'libtool-%s/libltdl' % self.version
        ]