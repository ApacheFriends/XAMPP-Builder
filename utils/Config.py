'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Config object encapsulate everything that
  is configurable like the download_dir or the
  build_dir.
'''

from ConfigParser import SafeConfigParser

class Config(object):

    def __init__(self, config_file, platform):
        self.config_file = config_file
        self.platform = platform

        self.configParser = SafeConfigParser()
        self.configParser.read([self.config_file])

    @property
    def download_dir(self):
        return self.configParser.get('XAMPP Builder', 'download_dir')

    @property
    def build_dir(self):
        return self.configParser.get('XAMPP Builder', 'build_dir')

