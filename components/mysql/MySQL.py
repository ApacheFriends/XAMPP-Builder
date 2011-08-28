"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The MySQL component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class MySQL(Component):

    def __init__(self, config):
        super(MySQL, self).__init__('MySQL', os.path.dirname(__file__), config)

        (major, minor, patch) = self.version.split('.')

        self.download_url = 'http://ftp.gwdg.de/pub/misc/mysql/Downloads/MySQL-%s.%s/mysql-%s.tar.gz' % (major, minor, self.version)
        self.includeDir = 'mysql'
        self.libDir = 'mysql'

        self.dependencies = [
            Dependency('ZLib', configureFlags=["--with-zlib-dir=${COMPONENT_PATH}"])
        ]

        self.patches = [
            'mysql.server.patch'
        ]

    def configureFlags(self):
        flags = super(MySQL, self).configureFlags()

        flags.extend([
            '--disable-assembler',
            '--enable-local-infile',
            '--with-mysqld-user=nobody',
            '--with-unix-socket-path=${PREFIX}/var/mysql/mysql.sock',
            '--with-extra-charsets=complex',
            '--libexecdir=${PREFIX}/sbin',
            '--datadir=${PREFIX}/share',
            '--localstatedir=${PREFIX}/var/mysql',
            '--infodir=${PREFIX}/info',
            '--includedir=${PREFIX}/include',
            '--mandir=${PREFIX}/man',
            '--with-plugins=max-no-ndb',
            '--enable-thread-safe-client',
            '--without-ssl',
            '--without-bench',
            '--without-man',
            '--without-docs',
            '--disable-dependency-tracking'
        ])

        return  flags
