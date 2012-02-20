"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Perl component.
"""
import shutil
import os.path

from subprocess import check_call

from utils.Component import Component
from utils.Sandbox import Sandbox

class Perl(Component):

    def __init__(self, config):
        super(Perl, self).__init__('Perl', os.path.dirname(__file__), config)

        self.download_url = 'http://www.cpan.org/src/perl-%s.tar.gz' % self.version

        self.buildSteps.extend([self.setupCPANP])

    def configureCommand(self):
        return 'bash'

    def configureFlags(self):
        return [
            './Configure',
            '-Dprefix=$PREFIX',
            '-A', 'ccdlflags="$ARCH_FLAGS"',
            '-A', 'ccflags="$ARCH_FLAGS"',
            '-A', 'cppflags="$ARCH_FLAGS"',
            '-A', 'ldflags="$ARCH_FLAGS"',
            '-A', 'lddlflags="$ARCH_FLAGS"',
            '-des'
        ]

    def setupCPANP(self, component, archs, builder):
        sandbox = Sandbox([self], builder)

        print("==> Setup CPANP")

        sandbox.setup()

        perl_lib = os.path.join(sandbox.path, 'xamppfiles', 'lib', 'perl5', self.version)

        # Install config files
        shutil.copy(
            os.path.join(self.resourcesPath, 'Config.pm'),
            os.path.join(perl_lib, 'CPAN/Config.pm')
        )

        if not os.path.isdir(os.path.join(perl_lib, 'CPANPLUS/Config')):
            os.makedirs(os.path.join(perl_lib, 'CPANPLUS/Config'))
        shutil.copy(
            os.path.join(self.resourcesPath, 'System.pm'),
            os.path.join(perl_lib, 'CPANPLUS/Config/System.pm')
        )

        check_call([os.path.join(sandbox.path, 'xamppfiles', 'bin/cpanp'),'s','selfupdate','core'])

        check_call([os.path.join(sandbox.path, 'xamppfiles', 'bin/perl'),
                    os.path.join(self.resourcesPath, 'upgrade_modules.pl')])

        modules = ['MLDBM', 'Digest::MD5', 'MLDBM::Sync', 'Apache::ASP']
        for module in modules:
            check_call([os.path.join(sandbox.path, 'xamppfiles', 'bin/cpanp'), 'i', module, '--skiptest', '--verbose'])

        shutil.rmtree(os.path.join(sandbox.path, 'xamppfiles', 'var'))

        changes = sandbox.changes()

        filesToCopy = list(changes['new'])
        filesToCopy.extend([ file['file'] for file in changes['changed'] ])

        for src in filesToCopy:
            dest = os.path.join(self.buildPath, src[1:])

            if not os.path.isdir(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))

            if os.path.exists(dest) and not os.access(dest, os.W_OK):
                check_call(['chmod', '+w', dest])

            shutil.copy(src, dest)

        sandbox.tearDown()
