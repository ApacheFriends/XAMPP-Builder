'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
'''

from optparse import OptionParser

import sys
import os
import os.path
import urllib

from utils.Config import Config
from components import KNOWN_COMPONENTS

class Builder(object):

    def __init__(self):
        self.config = None
        self.components = {}

    def run(self):
        (action, args) = self.parseComandolineArguments()

        self.setupComponents()

        if action == 'build':
            self.build(args)
        elif action == 'download':
            self.download(args)
        else:
            print "Unknown action '%s'" % action
            exit(1)

    def parseComandolineArguments(self):
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

        return (args[0], args[1:])

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

    def download(self, args):
        components = self.findComponents(args)
        
        for c in components:
            self.downloadComponent(c)

    def downloadComponent(self, c):
        '''
          Make sure the archive dir exists and
          is writeable.
        '''
        
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
            print "%s: Download already downloaded." % (c.name)

    def build(self, args):
        print 'Build component'
