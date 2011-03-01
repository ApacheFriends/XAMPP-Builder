'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Config object encapsulate everything that
  is configurable like the download_dir or the
  build_dir.
'''

from ConfigParser import SafeConfigParser

import os.path

class Config(object):

    def __init__(self, config_file, platform, rel_base=None):
        self.config_file = config_file
        self.platform = platform

        self.configParser = SafeConfigParser()
        self.configParser.read([self.config_file])
        
        '''
          If no base for relative paths is given,
          we use the dir in which the config resides
        '''
        if rel_base is None:
            rel_base = os.path.dirname(config_file)
        
        self.rel_base = os.path.abspath(rel_base)

    @property
    def archivesPath(self):
        return self.preparePath(self.configParser.get('XAMPP Builder', 'archives'))

    @property
    def build_dir(self):
        return self.preparePath(self.configParser.get('XAMPP Builder', 'build_dir'))
    
    '''
      Returns an normalised and absolut path for any path given.
    '''
    def preparePath(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.rel_base, path)
        
        return os.path.abspath(path)

