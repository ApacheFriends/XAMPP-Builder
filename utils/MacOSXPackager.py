"""
  XAMPP Builder
  Copyright 2011-2012 Apache Friends, GPLv2+ licensed
  ===================================================

"""

from plistlib import readPlist
from io import BytesIO
from utils.Packager import Packager
from subprocess import check_call
from tempfile import mkdtemp

import os.path

import subprocess
def check_output(*popenargs, **kwargs):
	if 'stdout' in kwargs:
		raise ValueError('stdout argument not allowed, it will be overridden.')
	process = subprocess.Popen(stdout=subprocess.PIPE, *popenargs, **kwargs)
	output, unused_err = process.communicate()
	retcode = process.poll()
	if retcode:
		cmd = kwargs.get("args")
		if cmd is None:
			cmd = popenargs[0]
		raise subprocess.CalledProcessError(retcode, cmd, output=output)
	return output

class CalledProcessError(Exception):
	def __init__(self, returncode, cmd, output=None):
		self.returncode = returncode
		self.cmd = cmd
		self.output = output
	def __str__(self):
		return "Command '%s' returned non-zero exit status %d" % (
			self.cmd, self.returncode)
# overwrite CalledProcessError due to `output` keyword might be not available
subprocess.CalledProcessError = CalledProcessError

class MacOSXPackager(Packager):
	
	
	def __init__(self, builder):
		super(MacOSXPackager, self).__init__(builder)
		
		self._workPath = None
	
	def resourcesPath(self):
		return os.path.join(os.path.dirname(__file__), 'resources')
	
	@property
	def workPath(self):
		if self._workPath is None:
			dir = mkdtemp(prefix="xampp-builder-packaging-")
			
			def remove_dir():
				if os.path.isdir(dir):
					shutil.rmtree(dir)

				atexit.register(remove_dir)
			
			self._workPath = dir

		return self._workPath

	
	def packXAMPP(self, version, xamppDMGPath):
		# Get template image
		# Convert it to rw and resize
		# Render new background
		# Copy xampp files
		# Unmount, convert to readonly with compression
		tmpDisk = os.path.join(self.workPath, 'xampp.sparseimage')
		
		print("=> Convert template to readwrite image")
		self.convertImage(os.path.join(self.resourcesPath(), 'template-normal.dmg'), tmpDisk, False)
		print("=> Make image big enough to fit XAMPP in it")
		self.resizeImage(tmpDisk, '1g')
		
		print("=> Mount image")
		(device, dir) = self.attachImage(tmpDisk)
		
		print("=> Copy XAMPP files")
		for name, c in self.builder.components.iteritems():
			if c.isBuild:
				self.builder.copyComponent(c, os.path.join(dir, 'XAMPP'), includeDevelopmentFiles=False)
		
		print("=> Set version")
		with open(os.path.join(dir, 'XAMPP', 'xamppfiles', 'lib', 'VERSION'), 'w') as f:
			f.write(version)
		
		print("=> Unmount image")
		self.detachImage(device)
		
		print("=> Compress and make image readonly")
		self.convertImage(tmpDisk, xamppDMGPath, True)
		
	
	def attachImage(self, imagePath):
		output = readPlist(BytesIO(check_output(['hdiutil', 'attach', '-plist', '-nobrowse', '-mountrandom', '/tmp', imagePath])))
		
		mount_dict = output['system-entities'][0]
		
		return (mount_dict['dev-entry'], mount_dict['mount-point'])
	
	def convertImage(self, image, destination, readOnly):
		if readOnly:
			check_call(['hdiutil', 'convert', '-ov', '-format', 'UDZO', image, '-imagekey', 'zlib-level=9', '-o', destination])
		else:
			check_call(['hdiutil', 'convert', '-ov', '-format', 'UDSP', image, '-o', destination])
	
	def resizeImage(self, image, size):
		check_call(['hdiutil', 'resize', '-size', size, image])
	
	def detachImage(self, device):
		check_call(['hdiutil', 'detach', '-force', device])
		