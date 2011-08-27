"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Config object encapsulate everything that
  is configurable like the download_dir or the
  build_dir.
"""

from ConfigParser import SafeConfigParser, NoOptionError

import os.path

class Config(object):

    def __init__(self, config_file, platform, rel_base=None):
        self.config_file = config_file
        self.platform = platform

        self.configParser = SafeConfigParser({
            'confdir': '%(prefix)s/etc'
        })
        self.configParser.read([self.config_file])
        
        ## If no base for relative paths is given, we use the dir in which the config resides
        if rel_base is None:
            rel_base = os.path.dirname(config_file)
        
        self.rel_base = os.path.abspath(rel_base)

    @property
    def archivesPath(self):
        return self.preparePath(self.configParser.get('XAMPP Builder', 'archives'))

    @property
    def buildsPath(self):
        return self.preparePath(self.configParser.get('XAMPP Builder', 'builds'))
    
    @property
    def prefixPath(self):
        return self.preparePath(self.configParser.get(self.platform, 'prefix'))
        
    @property
    def confdirPath(self):
        return self.preparePath(self.configParser.get(self.platform, 'confdir'))

    @property
    def defaultCFlags(self):
        cflags = ""

        try:
            cflags = ' '.join([cflags, self.configParser.get('XAMPP Builder', 'cflags')])
            cflags = ' '.join([cflags, self.configParser.get(self.platform, 'cflags')])
        except KeyError:
            pass

        return cflags

    @property
    def defaultLDFlags(self):
        ldflags = ''

        try:
            ldflags = ' '.join([ldflags, self.configParser.get('XAMPP Builder', 'ldflags')])
            ldflags = ' '.join([ldflags, self.configParser.get(self.platform, 'ldflags')])
        except NoOptionError:
            pass

        return ldflags

    @property
    def archs(self):
        raw = ""
        archs = []

        try:
            raw = self.configParser.get(self.platform, 'archs')
        except NoOptionError:
            pass

        for arch in raw.split(','):
            if len(arch.strip()):
                archs.extend([arch])

        return archs

    def preparePath(self, path):
        """
         Returns an normalised and absolut path for any path given.
        """
        if not os.path.isabs(path):
            path = os.path.join(self.rel_base, path)
        
        return os.path.abspath(path)

