"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
"""
import atexit
import collections
import json
import shutil
from stat import S_IRUSR, S_IRGRP, S_IXUSR, S_IWUSR, S_IXGRP, S_IROTH, S_IXOTH
import string
import sys
import os
import os.path
import urllib

from optparse import OptionParser, OptionGroup
from subprocess import check_call
from inspect import isfunction
from tempfile import mkdtemp

from utils.Config import Config
from utils.FileUniversalizer import MachOUniversalizer
from utils.file import digestsInPath, copytree
from components import KNOWN_COMPONENTS
from utils.Sandbox import Sandbox

from utils.MacOSXPackager import MacOSXPackager

chown_tool = """#!/usr/bin/python

import sys
import os
import os.path
import json

log_dir="${LOG_DIR}"

with open(os.path.join(log_dir, "chown.json"), "a") as f:
	info = {"args": sys.argv[1:], "pwd": os.getcwd()}
	json.dump(info, f)
	f.write(",\\n")

"""

chmod_tool = """#!/usr/bin/python

import sys
import os
import os.path
import json
from subprocess import check_call

log_dir="${LOG_DIR}"

with open(os.path.join(log_dir, "chmod.json"), "a") as f:
	info = {"args": sys.argv[1:], "pwd": os.getcwd()}
	json.dump(info, f)
	f.write(",\\n")

check_call(["/bin/chmod"] + sys.argv[1:])

"""

install_tool = """#!/usr/bin/python

import sys
import os
import os.path
import json
from subprocess import check_call

from optparse import OptionParser

log_dir="${LOG_DIR}"

parser = OptionParser()

parser.add_option("-b", action="store_true")
parser.add_option("-C", action="store_true")
parser.add_option("-c", action="store_true")
parser.add_option("-p", action="store_true")
parser.add_option("-S", action="store_true")
parser.add_option("-s", action="store_true")
parser.add_option("-v", action="store_true")

parser.add_option("-d", action="store_true", dest="make_dir")

parser.add_option("-m", dest="mode")
parser.add_option("-g", dest="group")
parser.add_option("-o", dest="owner")

(options, args) = parser.parse_args()

with open(os.path.join(log_dir, "install.json"), "a") as f:
	info = {"mode":options.mode, "group":options.group, "owner":options.owner, "pwd": os.getcwd(), "sources":args[:-1], "dest":args[-1]}
	json.dump(info, f)
	f.write(",\\n")

if options.make_dir:
	for d in args:
		os.makedirs(d)
else:
	check_call(["cp"] + args)

"""

# Helpers
def commonInDict(dictA, dictB):
	common = dict()
	uncommon_keys = []

	for key in dictA:
		if key in dictB and dictB[key] == dictA[key]:
			common[key] = dictA[key]
		else:
			uncommon_keys.extend([key])

	return common, uncommon_keys

def ignoreFilesSet(files, rel_to=None):
	def ignore_set(dir, dir_content):
		ignore = set()
		if rel_to is not None:
			dir = os.path.relpath(dir, rel_to)

		for file in files:
			(dir_component, file_component) = os.path.split(file)
			if (dir_component == dir and
				file_component in dir_content):
				ignore.add(file_component)

		return ignore

	return ignore_set

class Builder(object):

	def __init__(self):
		self.config = None
		self.components = {}
		self.fileUniversalizer = [MachOUniversalizer()]
		# the build dir of these will be deleted on exit, because
		# they are not clean
		self.uncleanComponents = []
		self.installToolchainPath = None

		atexit.register(self.cleanUp)

	def run(self):
		(action, args) = self.parseCommandlineArguments()
		
		self.setupComponents()

		if action == 'build':
			self.build(args)
		elif action == 'download':
			self.download(args)
		elif action == 'dep':
			self.dependencies(args)
		elif action == 'pack':
			self.pack(args)
		elif action == 'packDev':
			self.packDev(args)
		else:
			print "Unknown action '%s'" % action
			sys.exit(1)

	def parseCommandlineArguments(self):
		parser = OptionParser(usage="Usage: %prog [options] (download|build|dep [component(s)])|(pack version dest-file)|(packDev version dest-file)")

		parser.add_option("-c", "--config", dest="config",
						  default="default.ini",
						  help="The config used for building XAMPP.")

		parser.add_option("", "--no-clean-on-failure",
						  dest="no_clean_on_failure",
						  action="store_true", default=False,
						  help="Don't remove files the build fails.")
		
		group = OptionGroup(parser, "Dependency Options (dep)")

		group.add_option("", "--json", dest="json",
						  action="store_true", default=False,
						  help="Print dependency information as parsable json list.")
		group.add_option("", "--missing", dest="missing",
						  action="store_true", default=False,
						  help="Automaticlly add components that are not builded yet.")

		parser.add_option_group(group)

		(self.options, args) = parser.parse_args()

		if self.options.config is None:
			parser.error("Use -c to specify a config file!")
		else:
			self.config = Config(self.options.config, "Mac OS X")

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
				def reportHook(blocks, blockSize, totalSize):
					if totalSize == 0:
						totalSize = 1
					print "\r%s: Download '%s' %i%%" % (c.name, c.download_url, 100*blocks*blockSize/totalSize),

				urllib.urlretrieve(c.download_url, c.sourceArchiveFile  + '.temp', reportHook)
				os.rename(c.sourceArchiveFile  + '.temp', c.sourceArchiveFile)
				print "%s: Download '%s' done." % (c.name, c.download_url)
			except:
				print 'failed!'
				raise
		else:
			print "%s: Download already downloaded." % c.name

	def build(self, args):
		components = self.findComponents(args)

		self.setupInstallToolchain()

		for c in components:
			self.uncleanComponents.append(c)

			if c.supportsOnPassUniversalBuild or len(self.config.archs) <= 1:
				for step in c.buildSteps:
					if step == 'unpack':
						self.unpackComponent(c)
					elif step == 'patch':
						self.patchComponent(c)
					elif step == 'setupSandbox':
						self.setupBuildSandboxCommand(c)
					elif step == 'configure':
						self.runConfigureCommand(c, self.config.archs)
					elif step == 'build':
						self.runBuildCommand(c, self.config.archs)
					elif step == 'install':
						self.runInstallCommand(c, c.buildPath)
					elif step == 'tearDownSandbox':
						self.tearDownBuildSandboxCommand(c)
					elif step == 'universalize':
						# Universalize is not needed in one pass builds
						pass
					elif step == 'createManifest':
						self.createManifestAndClearLog(c)
					elif isinstance(step, collections.Callable):
						step(component=c, archs=self.config.archs, builder=self)
					else:
						raise StandardError("Don't now how to run step %s" % str(step))
			else:
				arch_build_dirs = {}

				for arch in self.config.archs:
					arch_build_dirs[arch] = mkdtemp(prefix="xampp-builder-%s-%s-" % (c.name, arch))

				def cleanUp(dirs):
					for (key, value) in dirs.iteritems():
						shutil.rmtree(value)

				atexit.register(cleanUp, arch_build_dirs)

				archDependentSteps = c.buildSteps[0:c.buildSteps.index('universalize')]
				archIndependentSteps = c.buildSteps[c.buildSteps.index('universalize'):]

				for arch in self.config.archs:
					if os.path.isdir(c.workingDir):
						shutil.rmtree(c.workingDir)
					os.mkdir(c.workingDir)

					for step in archDependentSteps:
						if step == 'unpack':
							self.unpackComponent(c)
						elif step == 'patch':
							self.patchComponent(c)
						elif step == 'setupSandbox':
							self.setupBuildSandboxCommand(c)
						elif step == 'configure':
							self.runConfigureCommand(c, archs=[arch])
						elif step == 'build':
							self.runBuildCommand(c, archs=[arch])
						elif step == 'install':
							self.runInstallCommand(c, c.buildPath)
						elif step == 'tearDownSandbox':
							self.tearDownBuildSandboxCommand(c)
						elif isinstance(step, collections.Callable):
							step(component=c, archs=[arch], builder=self)
						else:
							raise StandardError("Don't now how to run arch dependent step %s" % str(step))

				for step in archIndependentSteps:
					if step == 'universalize':
						self.universalizeComponent(c, arch_build_dirs)
					elif step == 'createManifest':
						self.createManifestAndClearLog(c)
					elif isinstance(step, collections.Callable):
						step(component=c, archs=self.config.archs, builder=self)
					else:
						raise StandardError("Don't now how to run step %s" % str(step))

			self.uncleanComponents.remove(c)


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

		tar_process.extend([c.sourceArchiveFile] + c.extraTarFlags())

		print("==> Unpack %s (work dir %s)" % (c.name, c.workingDir))
		check_call(tar_process)

	def patchComponent(self, c):
		if not len(c.patches):
			return

		print("==> Patch %s" % c.name)
		os.chdir(c.workingDir)

		for patch in c.patches:
			if patch.endswith('.zip'):
				check_call(['unzip','-o', os.path.join(c.patches_dir, patch), '-d', '.'])
			elif patch.endswith('.patch'):
				check_call(['patch', '-p0', '-i', os.path.join(c.patches_dir, patch)])
			else:
				raise StandardError("Do not know how to apply %s" % patch)

	def runConfigureCommand(self, c, archs):
		commandArguments = []

		command = c.configureCommand()
		commandArguments.extend(c.computedConfigureFlags())
		environment = dict(os.environ)
		
		# TODO: This was commented out, why?
		environment['PATH'] = "%s/bin:%s" % (self.installToolchainPath, environment['PATH'])

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

		print("==> Configure %s %s" % (c.name, environment))
		check_call([command] + commandArguments, env=environment)

	def runBuildCommand(self, c, archs):
		commandArguments = []

		command = c.buildCommand()
		commandArguments.extend(c.computedBuildFlags())
		environment = dict(os.environ)
		environment['PATH'] = "%s/bin:%s" % (self.installToolchainPath, environment['PATH'])

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
		environment['PATH'] = "%s/bin:%s" % (self.installToolchainPath, environment['PATH'])

		for (key, value) in c.installEnvironment().iteritems():
			environment[key] = string.Template(value).safe_substitute({'DEST_DIR': dest_dir})

		commandArguments = map(lambda x: string.Template(x).safe_substitute({'DEST_DIR': dest_dir}), commandArguments)

		print("==> Install %s (to %s)" % (c.name, dest_dir))
		check_call([command] + commandArguments, env=environment)

	def universalizeComponent(self, c, arch_build_dirs):
		digests = {}

		print("==> Universalize %s" % c.name)

		for arch, path in arch_build_dirs.iteritems():
			digests[arch] = digestsInPath(path)

		common_dict = digests[digests.keys()[0]]

		arch_depend_files = []

		for arch in digests:
			(common_dict, depend) = commonInDict(common_dict, digests[arch])

			arch_depend_files.extend(depend)

		if os.path.isdir(c.buildPath):
			shutil.rmtree(c.buildPath)

		# Copy the common files
		src = arch_build_dirs[arch_build_dirs.keys()[0]]
		shutil.copytree(src,
						c.buildPath,
						symlinks=True,
						ignore=ignoreFilesSet(arch_depend_files, rel_to=src))

		for file in arch_depend_files:
			success = False

			for universalizer in self.fileUniversalizer:
				if universalizer.applicableTo(file, arch_build_dirs):
					success = universalizer.universalizeFile(file, os.path.join(c.buildPath, file), arch_build_dirs)

					break

			if success is False:
				raise StandardError("Could not universalize %s (%s)" % (file, arch_build_dirs))

	def componentsDependingOn(self, component):
		dependents = []

		for c in self.components.values():
			for d in c.dependencies:
				if d.componentName.lower() == component.name.lower():
					dependents.append(c)

		return dependents

	def dependencies(self, args):
		if not len(args):
			components_to_consider = []
		else:
			components_to_consider = self.findComponents(args)

		if self.options.missing:
			for c in self.components.values():
				if not c.isBuild:
					components_to_consider.append(c)

		# Find all components that are directly or indirectly
		# depended on these components

		foundNew = True

		while foundNew:
			foundNew = False

			for c in components_to_consider:
				dependents = self.componentsDependingOn(c)

				for d in dependents:
					if d not in components_to_consider:
						components_to_consider.append(d)
						foundNew = True


		resolved = []
		unhandled = list(set(components_to_consider))

		while len(unhandled):
			for c in unhandled:
				satisfied = True

				for d in c.dependencies:
					if self.findComponent(d.componentName) not in resolved and \
						self.findComponent(d.componentName) in unhandled:
						satisfied = False

				if satisfied:
					resolved.append(c)
					unhandled.remove(c)

		if self.options.json:
			print(json.dumps([c.name.lower() for c in resolved]))
		else:
			for c in resolved:
				print(c.name.lower())

	def copyComponent(self, c, dest=None, includeDevelopmentFiles=True):
		if dest is None:
			dest = self.config.prefixPath
		
		manifest = None
		with open(c.manifestPath, 'r') as f:
			manifest = json.load(f)
		
		files = manifest['release'].keys()
		
		if includeDevelopmentFiles:
			files.append(manifest['dev'].keys())
		
		for file in files:
			srcFile = os.path.join(c.buildPath, file[1:])
			destFile = os.path.join(dest, os.path.relpath(file, self.config.destPath))
			
			if os.path.islink(srcFile):
				linkto = os.readlink(srcFile)
				os.symlink(linkto, destFile)
			elif os.path.isdir(srcFile):
				if not os.path.isdir(destFile):
					os.makedirs(destFile)
			else:
				shutil.copy2(srcFile, destFile)
	
	def cleanUp(self):
		if self.installToolchainPath:
			if self.options.no_clean_on_failure:
				print("Wanring: won't remove %s..." % self.installToolchainPath)
			else:
				shutil.rmtree(self.installToolchainPath, ignore_errors=True)
		
		
		for c in self.uncleanComponents:
			if self.options.no_clean_on_failure:
				print("Wanring: won't remove %s..." % c.buildPath)
			else:
				shutil.rmtree(c.buildPath, ignore_errors=True)

	def setupInstallToolchain(self):
		self.installToolchainPath = mkdtemp(prefix="xampp-builder-install-toolchain")

		os.mkdir(os.path.join(self.installToolchainPath, "bin"))

		log_dir = os.path.join(self.installToolchainPath, "logs")

		os.mkdir(log_dir)

		mode755 = S_IRUSR|S_IWUSR|S_IXUSR|S_IRGRP|S_IXGRP|S_IROTH|S_IXOTH

		with open(os.path.join(self.installToolchainPath, "bin", "chmod"), "w") as f:
			f.write(string.Template(chmod_tool).safe_substitute({"LOG_DIR": log_dir}))

		os.chmod(os.path.join(self.installToolchainPath, "bin", "chmod"), mode755)

		with open(os.path.join(self.installToolchainPath, "bin", "chown"), "w") as f:
			f.write(string.Template(chown_tool).safe_substitute({"LOG_DIR": log_dir}))

		os.chmod(os.path.join(self.installToolchainPath, "bin", "chown"), mode755)

		with open(os.path.join(self.installToolchainPath, "bin", "install"), "w") as f:
			f.write(string.Template(install_tool).safe_substitute({"LOG_DIR": log_dir}))

		os.chmod(os.path.join(self.installToolchainPath, "bin", "install"), mode755)
	
	def createManifestAndClearLog(self, component):
		manifest={'dev': {}, 'release':{}}
		
		chmodLogFile = os.path.join(self.installToolchainPath, "logs", 'chmod.json')
		chownLogFile = os.path.join(self.installToolchainPath, "logs", 'chown.json')
		installLogFile = os.path.join(self.installToolchainPath, "logs", 'install.json')
		
		chmodManifest = self.manifestFromChmodLog(chmodLogFile)
		chownManifest = self.manifestFromChownLog(chownLogFile)
		installManifest = self.manifestFromInstallLog(installLogFile)
		
		for root, dirs, files in os.walk(component.buildPath):
			for dirname in dirs:
				dir = os.path.join(root, dirname)
				
				user=None
				group=None
				mode=None
				
				if dir in chmodManifest:
					mode = chmodManifest[dir]['mode']
					
				if dir in chownManifest:
					if 'user' in chownManifest[dir]:
						user = chownManifest[dir]['user']
					if 'group' in chownManifest[dir]:
						group = chownManifest[dir]['group']
						
				if dir in installManifest:
					if 'user' in installManifest[dir]:
						user = installManifest[dir]['user']
					if 'group' in installManifest[dir]:
						group = installManifest[dir]['group']
					if 'mode' in installManifest[dir]:
						mode = installManifest[dir]['mode']
				
				if user is None:
					user = 'nobody'
				if group is None:
					group = 'nogroup'
				if mode is None:
					mode = '755'
				
				installPath = '/' + os.path.relpath(dir, component.buildPath)
				
				if not installPath.startswith(self.config.destPath):
					continue
				
				if component.isPathDevelopmentOnly(installPath):
					manifest['dev'][installPath] = {
						'user': user,
						'group': group,
						'mode': mode
					}
				else:
					manifest['release'][installPath] = {
						'user': user,
						'group': group,
						'mode': mode
					}
			
			for filename in files:
				file = os.path.join(root, filename)
				
				user=None
				group=None
				mode=None
				
				if file in chmodManifest:
					mode = chmodManifest[file]['mode']
					
				if file in chownManifest:
					if 'user' in chownManifest[file]:
						user = chownManifest[file]['user']
					if 'group' in chownManifest[file]:
						group = chownManifest[file]['group']
						
				if file in installManifest:
					if 'user' in installManifest[file]:
						user = installManifest[file]['user']
					if 'group' in installManifest[file]:
						group = installManifest[file]['group']
					if 'mode' in installManifest[file]:
						mode = installManifest[file]['mode']
				
				if user is None:
					user = 'nobody'
				if group is None:
					group = 'nogroup'
				if mode is None:
					mode = '644'
				
				installPath = '/' + os.path.relpath(file, component.buildPath)
				
				if not installPath.startswith(self.config.destPath):
					continue
				
				if component.isPathDevelopmentOnly(installPath):
					manifest['dev'][installPath] = {
						'user': user,
						'group': group,
						'mode': mode
					}
				else:
					manifest['release'][installPath] = {
						'user': user,
						'group': group,
						'mode': mode
					}
			
		
		with open(component.manifestPath, 'w') as f:
			json.dump(manifest, f);
		
		if os.path.isfile(chmodLogFile):
			os.remove(chmodLogFile)
		if os.path.isfile(chownLogFile):
			os.remove(chownLogFile)
		if os.path.isfile(installLogFile):
			os.remove(installLogFile)
	
	def manifestFromChmodLog(self, chmodLogFile):
		logContent = None
		manifest = {}
		
		if not os.path.isfile(chmodLogFile):
			return manifest;
		
		with open(chmodLogFile, 'r') as f:
			string = f.read()
			logContent = json.loads('[' + string + 'null]')
		
		if logContent is not None:
			for command in logContent:
				files=[]
				mode=None
				recursive=False
				
				if command is None:
					continue
				
				for arg in command['args']:
					if arg == '-R' or arg == '-r':
						recursive=True
					elif arg.startswith('-'):
						# Ignore all options for now
						continue
					elif mode is None:
						mode = arg
					else:
						file = os.path.join(command['pwd'], arg)
						files.append(file)
						if recursive:
							files.extend(self.listOfPathsBelow(file))
				
				for file in files:
					if file not in manifest:
						manifest[file] = {}
					
					manifest[file]['mode'] = mode
		
		return manifest
	
	def manifestFromChownLog(self, chmodLogFile):
		logContent = None
		manifest = {}
		
		if not os.path.isfile(chmodLogFile):
			return manifest;
		
		with open(chmodLogFile, 'r') as f:
			string = f.read()
			logContent = json.loads('[' + string + 'null]')
		
		if logContent is not None:
			for command in logContent:
				files=[]
				user=None
				group=None
				recursive=False
				
				if command is None:
					continue
				
				for arg in command['args']:
					if arg == '-R' or arg == '-r':
						recursive=True
					elif arg.startswith('-'):
						# Ignore all options for now
						continue
					elif user is None and group is None:
						(user, group) = arg.split(':')
					else:
						file = os.path.join(command['pwd'], arg)
						files.append(file)
						if recursive:
							files.extend(self.listOfPathsBelow(file))
				
				
				for file in files:
					if file not in manifest:
						manifest[file] = {}
					
					if len(user) > 0:
						manifest[file]['user'] = user
					if group is not None and len(group) > 0:
						manifest[file]['group'] = group
		
		return manifest
	
	def manifestFromInstallLog(self, chmodLogFile):
		logContent = None
		manifest = {}
		
		if not os.path.isfile(chmodLogFile):
			return manifest;
		
		with open(chmodLogFile, 'r') as f:
			string = f.read()
			logContent = json.loads('[' + string + 'null]')
		
		if logContent is not None:
			for command in logContent:
				files=[]
				
				if command is None:
					continue

				user=command['owner']
				group=command['group']
				mode=command['mode']
				sources=command['sources']
				dest=command['dest']
				
				if len(sources) > 1 or dest.endswith('/'):
					for file in sources:
						files.append(os.path.join(dest, os.path.basename(file)))
				else:
					files.append(dest)
				
				
				for file in files:
					if file not in manifest:
						manifest[file] = {}
					
					if user is not None and len(user) > 0:
						manifest[file]['user'] = user
					if group is not None and len(group) > 0:
						manifest[file]['group'] = group
					if mode is not None and len(mode) > 0:
						manifest[file]['mode'] = mode
		
		return manifest

	def listOfPathsBelow(self, path):
		paths=[]
		
		for root, dirs, files in os.walk(path):
			for dir in dirs:
				paths.append(os.path.join(root, dir))
			for file in files:
				paths.append(os.path.join(root, file))
		
		return paths

	def setupBuildSandboxCommand(self, component):
		self.sandbox = Sandbox([d.componentName for d in component.dependencies], self)

		print("==> Setup build sandbox")

		self.sandbox.setup()

	
	def tearDownBuildSandboxCommand(self, component):
		if self.sandbox:
			print("==> Tear down build sandbox")
			self.sandbox.tearDown()
			self.sandbox = None
	
	def pack(self, args):
		packager = MacOSXPackager(self)
		
		version=args[0]
		destPath=args[1]
		
		packager.packXAMPP(version, destPath)
