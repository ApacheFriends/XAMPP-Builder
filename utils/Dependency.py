"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

"""

import os.path
from string import Template
from utils.Component import Component

class Dependency(object):
    
    def __init__(self, componentName, configureFlags=None, cFlags=None, ldFlags=None, environment=None):
        assert componentName is not None

        if not configureFlags:
            configureFlags = []

        if not cFlags:
            cFlags = []

        if not ldFlags:
            ldFlags = []

        if not environment:
            environment = {}

        self.configureFlags = configureFlags
        self.componentName = componentName
        self.cFlags = cFlags
        self.ldFlags = ldFlags
        self.environment = environment

    def computedConfigureFlags(self, builder, forComponent):
        return self.computeValue(self.configureFlags, builder, forComponent)

    def computedCFlags(self, builder, forComponent):
        return self.computeValue(self.cFlags, builder, forComponent)

    def computedLDFlags(self, builder, forComponent):
        return self.computeValue(self.ldFlags, builder, forComponent)

    def computedEnvironment(self, builder, forComponent):
        return self.computeValue(self.environment, builder, forComponent)

    def computeValue(self, value, builder, forComponent):
        component = builder.findComponent(self.componentName)

        if not isinstance(component, Component):
            raise StandartError("Did not found a valid component for '%s'. Got '%s'" % (self.componentName, component))

        c_root = os.path.join(component.buildPath, builder.config.prefixPath[1:])

        vars = {
            'COMPONENT_PATH': c_root,
            'INCLUDE_PATH': os.path.join(c_root, 'include', component.includeDir or ''),
            'LIB_PATH': os.path.join(c_root, 'lib', component.libDir or '')
        }

        return map(lambda x: Template(x).substitute(vars), value)
