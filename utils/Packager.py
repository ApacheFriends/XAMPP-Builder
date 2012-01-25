"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

"""

class Packager(object):
	
	def __init__(self, builder):
		self.builder = builder
	
	def pack(self, version, xamppPath, devPath, outputDirectory):
		raise RuntimeError("Not implemented.")