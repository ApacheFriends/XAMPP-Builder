"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The ProFTPd component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class ProFTPd(Component):

    def __init__(self, config):
        super(ProFTPd, self).__init__('ProFTPd', os.path.dirname(__file__), config)

        self.download_url = 'ftp://ftp.proftpd.org/distrib/source/proftpd-%s.tar.gz' % self.version

        self.dependencies = [
            Dependency('ZLib', cFlags=['-I${INCLUDE_PATH}'], ldFlags=['-L${LIB_PATH}']),
            Dependency('Ncurses', cFlags=['-I${INCLUDE_PATH}'], ldFlags=['-L${LIB_PATH}']),
            Dependency('OpenSSL', cFlags=['-I${INCLUDE_PATH}'], ldFlags=['-L${LIB_PATH}']),
            Dependency('MySQL', cFlags=['-I${INCLUDE_PATH}'], ldFlags=['-L${LIB_PATH}'])
        ]

    def configureFlags(self):
        flags = super(ProFTPd, self).configureFlags()

        flags.extend([
            '--with-modules=mod_sql:mod_sql_mysql:mod_tls'
        ])

        return  flags
