"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
"""
import atexit
import shutil
import string
import sys
import os
import os.path
from tempfile import mkdtemp
import urllib

from optparse import OptionParser
from subprocess import check_call

from utils.Config import Config
from components import KNOWN_COMPONENTS

class Builder(object):

    def __init__(self):
        self.config = None
        self.components = {}

    def run(self):
        (action, args) = self.parseCommandlineArguments()

        self.setupComponents()

        if action == 'build':
            self.build(args)
        elif action == 'download':
            self.download(args)
        else:
            print "Unknown action '%s'" % action
            sys.exit(1)

    def parseCommandlineArguments(self):
        parser = OptionParser()

        parser.add_option("-c", "--config", dest="config",
                          default="default.ini",
                          help="The config used for building XAMPP.")

        (options, args) = parser.parse_args()

        if options.config is None:
            parser.error("Use -c to specify a config file!")
        else:
            self.config = Config(options.config, "Mac OS X")

        if len(args) < 1:
            parser.error("Specify an action!")

        return args[0], args[1:]

    def substituteArchVariables(self, s, archs):
        vars = {
            'ARCH_FLAGS': ' '.join(['-arch %s' % arch for arch in archs]),
        }

        if len(archs) == 1:
            vars['ARCH'] = archs[0]
        else:
            vars['ARCH'] = 'universal'

        return string.Template(s).safe_substitute(vars)

    def setupComponents(self):
        
        for c in KNOWN_COMPONENTS:
            print 'debug: instantiate %s' % c
            
            component = c(config=self.config)
            
            if component.name in self.components:
                raise StandardError('Try to register %s twice!' % component.name)
                
            self.components[component.name] = component


    def findComponents(self, args):
        if len(args) == 0 or 'all' in args:
            return self.components.values()
        
        args = map(lambda x: x.lower(), args)
        components = []
        
        for (key, value) in self.components.iteritems():
            if key.lower() in args:
                components.append(value)

        return components

    def findComponent(self, componentName):
        assert componentName is not None
        
        componentList = self.findComponents([componentName])

        if not len(componentList):
            return None
        else:
            return componentList[0]

    def download(self, args):
        components = self.findComponents(args)
        
        for c in components:
            self.downloadComponent(c)

    def downloadComponent(self, c):
        """
          Make sure the archive dir exists and
          is writeable.
        """

        if not os.path.isdir(self.config.archivesPath):
            os.mkdir(self.config.archivesPath)
        
        if not os.path.exists(c.sourceArchiveFile):
            print "%s: Download '%s'..." % (c.name, c.download_url),
            sys.stdout.flush()
            try:
                urllib.urlretrieve(c.download_url, c.sourceArchiveFile  + '.temp')
                os.rename(c.sourceArchiveFile  + '.temp', c.sourceArchiveFile)
                print 'done.'
            except:
                print 'failed!'
                raise
        else:
            print "%s: Download already downloaded." % c.name

    def build(self, args):
        components = self.findComponents(args)

        for c in components:

            if c.supportsOnPassUniversalBuild or len(self.config.archs) <= 1:
                self.unpackComponent(c)
                self.runConfigureCommand(c, self.config.archs)
                self.runBuildCommand(c, self.config.archs)
                self.runInstallCommand(c, c.buildPath)
            else:
                arch_build_dirs = {}

                for arch in self.config.archs:
                    arch_build_dirs[dir] = mkdtemp(prefix="xampp-builder-%s-%s-" % (c.name, arch))

                def cleanUp(dirs):
                    for (key, value) in dirs.iteritems():
                        shutil.rmtree(value)

                atexit.register(cleanUp, arch_build_dirs)

                for arch in self.config.archs:
                    if os.path.isdir(c.workingDir):
                        shutil.rmtree(c.workingDir)
                    os.mkdir(c.workingDir)

                    self.unpackComponent(c)
                    self.runConfigureCommand(c, archs=[arch])
                    self.runBuildCommand(c, archs=[arch])
                    self.runInstallCommand(c, arch_build_dirs[dir])



    def unpackComponent(self, c):
        # Change our working dir to the source dir
        os.chdir(c.workingDir)

        tar_process = ['/usr/bin/tar']
        (path, ext) = os.path.splitext(c.sourceArchiveFile)

        if ext == '.gz' or ext == '.tgz' or ext == '.Z':
            tar_process.append('xpzf')
        elif ext == '.bz2':
            tar_process.append('xpjf')
        elif ext == '.tar':
            tar_process.append('xpf')
        else:
            raise StandardError('Unknown archive format')

        tar_process.extend([c.sourceArchiveFile,
                            '--strip', '1'])

        print("==> Unpack %s (work dir %s)" % (c.name, c.workingDir))
        check_call(tar_process)

    def runConfigureCommand(self, c, archs):
        commandArguments = []

        command = c.configureCommand()
        commandArguments.extend(c.computedConfigureFlags())
        environment = dict(os.environ)

        for (key, value) in c.configureEnvironment().iteritems():
            environment[key] = value

        for d in c.dependencies:
            commandArguments.extend(d.computedConfigureFlags(self, c))
            oldCFlags = ""
            oldLDFlags = ""
            
            try:
                oldCFlags = environment['CFLAGS']
                oldLDFlags = environment['LDFLAGS']
            except KeyError:
                pass

            environment['CFLAGS'] = ' '.join([oldCFlags] + d.computedCFlags(self, c))
            environment['LDFLAGS'] = ' '.join([oldLDFlags] + d.computedLDFlags(self, c))

        commandArguments = map(lambda x: self.substituteArchVariables(x, archs), commandArguments)

        for key in environment.copy():
            environment[key] = self.substituteArchVariables(environment[key], archs)

        print("==> Configure %s" % c.name)
        check_call([command] + commandArguments, env=environment)

    def runBuildCommand(self, c, archs):
        commandArguments = []

        command = c.buildCommand()
        commandArguments.extend(c.computedBuildFlags())
        environment = dict(os.environ)

        for (key, value) in c.buildEnvironment().iteritems():
            environment[key] = value

        for d in c.dependencies:
            oldCFlags = ""
            oldLDFlags = ""

            try:
                oldCFlags = environment['CFLAGS']
                oldLDFlags = environment['LDFLAGS']
            except KeyError:
                pass

            environment['CFLAGS'] = ' '.join([oldCFlags] + d.computedCFlags(self, c))
            environment['LDFLAGS'] = ' '.join([oldLDFlags] + d.computedLDFlags(self, c))

        commandArguments = map(lambda x: self.substituteArchVariables(x, archs), commandArguments)

        for key in environment.copy():
            environment[key] = self.substituteArchVariables(environment[key], archs)

        print("==> Build %s" % c.name)
        check_call([command] + commandArguments, env=environment, shell=True)

    def runInstallCommand(self, c, dest_dir):
        commandArguments = []

        command = c.installCommand()
        commandArguments.extend(c.computedInstallFlags())
        environment = dict(os.environ)

        for (key, value) in c.installEnvironment().iteritems():
            environment[key] = string.Template(value).safe_substitute({'DEST_DIR': dest_dir})

        commandArguments = map(lambda x: string.Template(x).safe_substitute({'DEST_DIR': dest_dir}), commandArguments)

        print("==> Install %s (to %s)" % (c.name, dest_dir))
        check_call([command] + commandArguments, env=environment)
