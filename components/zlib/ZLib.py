"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================
  
  The ZLib component.
"""

from utils.Component import Component

import os.path

class ZLib(Component):
    
    def __init__(self, config):
        super(ZLib, self).__init__('ZLib', os.path.dirname(__file__), config)
        
        self.download_url = 'http://www.zlib.net/zlib-%s.tar.gz' % self.version
        
    

