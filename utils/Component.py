'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  This class encapsulate every component that can
  be build or whatsoever.
'''

import os.path
import string

class Component(object):

    def __init__(self, name, path, config):
        assert name != None
        assert config != None

        self.name = name
        self.config = config
        self.download_url = None
        
        '''
          Read the version of this component.
        '''
        version_file = os.path.join(path, 'version')
        
        if not os.path.exists(version_file):
            raise StandardError("Version file '%s' for '%s' does not exists!" % (version_file, self.name))
        
        with open(version_file, 'r') as f:
            self.version = f.readline().strip(' \n\r\t')
    
    '''
      Returns the flags used for configure or
      cmake. Flags from dependencies are added
      to this later. Possible variables are
      substituted later.
    '''
    def configureFlags(self):
        return [
            '--prefix=$PREFIX', 
            '--sysconfdir=$SYSCONFDIR'
        ]
        
    '''
      Returns the fully computable flags which can be
      passed in quotes and joined with an space to
      configure or cmake or whatever.
    '''
    def computedConfigureFlags(self):
        return map(lambda x: self.substituteCommonVariables(x), self.configureFlags())
    
    def substituteCommonVariables(self, s):
        vars = {
            'PREFIX': self.config.prefixPath,
            'SYSCONFDIR': self.config.confdirPath
        }
        return string.Template(s).safe_substitute(vars)
    
    @property
    def sourceArchivePath(self):
        archive_ext = None
        (j, filename) = os.path.split(self.download_url)
        
        if filename.endswith('.tar.gz') or filename.endswith('.tgz') or filename.endswith('.tar.Z'):
            archive_ext = 'tar.gz'
        elif filename.endswith('.tar.bz2'):
            archive_ext = 'tar.bz2'
        elif filename.endswith('.tar'):
            archive_ext = 'tar'
        else:
            raise StandardError("Unknown archive format '%s'" % ext)
        
        return os.path.join(self.config.archivesPath, '%s-%s.%s' % (self.name.lower(), self.version, archive_ext))
    
    @property
    def buildPath(self):
        return os.path.join(self.config.buildsPath, self.name.lower())
        
        
