"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
"""
import os
import shutil
from utils.Component import Component
from utils.Differences import differencesBetweenDigests
from utils.file import digestsInPath

class Sandbox(object):

    def __init__(self, componentsToUse, builder):
        self.componentsToUse = set()
        self.builder = builder

        for c in componentsToUse:
            if isinstance(c, str):
                i = self.builder.findComponent(c)

                if not i:
                    raise StandardError("Component %s not found" % c)

                self.componentsToUse.add(i)
            elif isinstance(c, Component):
                self.componentsToUse.add(c)

        # Recursively add dependencies
        oldSet = None

        while oldSet != self.componentsToUse:
            oldSet = self.componentsToUse.copy()
            print("Old %s!=%s" % (str(oldSet), str(self.componentsToUse)))
            for c in oldSet:
                for d in c.dependencies:
                    self.componentsToUse.add(self.builder.findComponent(d.componentName))

        self._path = builder.config.prefixPath
        self.isSetup = False

    @property
    def path(self):
        return self._path

    def setup(self):
        assert not self.isSetup

        self.isSetup = True

        if os.path.isdir(self.path):
            raise StandardError("Sandbox path already exists %s" % self.path)

        for c in self.componentsToUse:
            self.builder.copyComponent(c, self.path)

        self.initialDigests = digestsInPath(self.path, relative=False)

    def changes(self):
        assert self.isSetup

        digests = digestsInPath(self.path, relative=False)

        return differencesBetweenDigests(self.initialDigests, digests)

    def tearDown(self):
        assert self.isSetup

        self.isSetup = False

        shutil.rmtree(self.path)

