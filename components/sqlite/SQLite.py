"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================
  
  The SQLite component.
"""

from utils.Component import Component

import os.path

class SQLite(Component):
    
    def __init__(self, config):
        super(SQLite, self).__init__('SQLite', os.path.dirname(__file__), config)

        self.download_url = 'http://www.sqlite.org/sqlite-autoconf-%s.tar.gz' % self.version

    def installFlags(self):
        return [
            "install",
            "prefix=${DEST_DIR}"
        ]

