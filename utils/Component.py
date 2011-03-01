'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  This class encapsulate every component that can
  be build or whatsoever.
'''

import os.path

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
        
        
