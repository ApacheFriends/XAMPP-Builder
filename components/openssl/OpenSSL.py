"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The OpenSSL component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class OpenSSL(Component):

    def __init__(self, config):
        super(OpenSSL, self).__init__('OpenSSL', os.path.dirname(__file__), config)

        self.download_url = 'http://www.openssl.org/source/openssl-%s.tar.gz' % self.version
        self.supportsOnPassUniversalBuild = False
        self.dependencies = [
            Dependency('ZLib')
        ]

    def configureFlags(self):
        return [
            './Configure',
            '--prefix=$PREFIX',
            '--openssldir=${PREFIX}/share/openssl',
            'shared',
            'darwin-${ARCH}-cc'
        ]

    def installFlags(self):
        return [
            "install",
            "INSTALL_PREFIX=${DEST_DIR}"
        ]

    def configureCommand(self):
        return 'bash'

