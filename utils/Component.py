"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  This class encapsulate every component that can
  be build or whatsoever.
"""

import atexit
import os.path
import shutil
import string

from tempfile import mkdtemp

class Component(object):

    def __init__(self, name, path, config):
        assert name is not None
        assert config is not None

        self.name = name
        self.config = config
        self.download_url = None
        self.dependencies = []
        self._workingDir = None
        self.supportsOnPassUniversalBuild = True
        self.patches = []
        self.patches_dir = os.path.join(path, 'patches')
        # Rel to includes/
        self.includeDir = None
        self.libDir = None

        self.buildSteps = [
            'unpack',
            'patch',
            'configure',
            'build',
            'install',
            'universalize'
        ]

        # Read the version of this component.
        version_file = os.path.join(path, 'version')
        
        if not os.path.exists(version_file):
            raise StandardError("Version file '%s' for '%s' does not exists!" % (version_file, self.name))
        
        with open(version_file, 'r') as f:
            self.version = f.readline().strip(' \n\r\t')

    def configureFlags(self):
        """
          Returns the flags used for configure or cmake. Flags from dependencies are added to this later. Possible
          variables are substituted later.
        """
        return [
            '--prefix=$PREFIX', 
            '--sysconfdir=$SYSCONFDIR'
        ]

    def computedConfigureFlags(self):
        """
          Returns the fully computable flags which can be passed in quotes and joined with an space to configure or
          cmake or whatever.
        """
        return map(lambda x: self.substituteCommonVariables(x), self.configureFlags())

    def configureEnvironment(self):
        """
          Returns the environment for the configure or cmake command.
        """
        return {
            "CC": "gcc $ARCH_FLAGS",
            "CXX": "g++ $ARCH_FLAGS",
            "CPP": "cpp",
            "CXXCPP": "cpp"
        }
    
    def configureCommand(self):
        return './configure'
    
    def substituteCommonVariables(self, s):
        vars = {
            'PREFIX': self.config.prefixPath,
            'SYSCONFDIR': self.config.confdirPath,
        }

        return string.Template(s).safe_substitute(vars)

    def buildCommand(self):
        return 'make'

    def buildEnvironment(self):
        return self.configureEnvironment()

    def buildFlags(self):
        return []

    def computedBuildFlags(self):
        return map(lambda x: self.substituteCommonVariables(x), self.buildFlags())

    def installCommand(self):
        return 'make'

    def installEnvironment(self):
        return self.buildEnvironment()

    def installFlags(self):
        return [
            "install",
            "DESTDIR=${DEST_DIR}"
        ]

    def computedInstallFlags(self):
        return map(lambda x: self.substituteCommonVariables(x), self.installFlags())

    def extraTarFlags(self):
        return [
            '--strip', '1'
        ]

    @property
    def sourceArchiveFile(self):
        archive_ext = None
        (j, filename) = os.path.split(self.download_url)
        
        if filename.endswith('.tar.gz') or filename.endswith('.tgz') or filename.endswith('.tar.Z'):
            archive_ext = 'tar.gz'
        elif filename.endswith('.tar.bz2'):
            archive_ext = 'tar.bz2'
        elif filename.endswith('.tar'):
            archive_ext = 'tar'
        else:
            raise StandardError("Unknown archive format '%s'" % archive_ext)
        
        return os.path.join(self.config.archivesPath, '%s-%s.%s' % (self.name.lower(), self.version, archive_ext))

    @property
    def workingDir(self):
        if self._workingDir is None:
            self._workingDir = mkdtemp(prefix="xampp-builder-%s-" % self.name)

        # Temporary save the working dir here
        dir = self._workingDir

        def remove_dir():
            if os.path.isdir(dir):
                shutil.rmtree(dir)

        atexit.register(remove_dir)

        return self._workingDir

    @property
    def buildPath(self):
        return os.path.join(self.config.buildsPath, self.name.lower())
        
        
