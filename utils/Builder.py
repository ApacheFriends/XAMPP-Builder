'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
'''

from optparse import OptionParser

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
        else:
            print "Unknown action '%s'" % action
            exit(1)

    def parseComandolineArguments(self):
	parser = OptionParser()

        parser.add_option("-c", "--config", dest="config",
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

    def build(self, args):
        print 'Build component'
