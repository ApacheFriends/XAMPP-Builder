"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The MySQL component.
"""
import shutil
from subprocess import check_call

from utils.Component import Component
from utils.Dependency import Dependency

import os.path
from utils.Sandbox import Sandbox

class MySQL(Component):

    def __init__(self, config):
        super(MySQL, self).__init__('MySQL', os.path.dirname(__file__), config)

        (major, minor, patch) = self.version.split('.')

        self.download_url = 'http://ftp.gwdg.de/pub/misc/mysql/Downloads/MySQL-%s.%s/mysql-%s.tar.gz' % (major, minor, self.version)
        self.includeDir = 'mysql'
        self.libDir = 'mysql'

        self.dependencies = [
            Dependency('ZLib', configureFlags=["-DWITH_ZLIB=${COMPONENT_PATH}"])
        ]

        self.patches = [
            'mysql.server.patch'
        ]

        self.buildSteps.extend([self.completeInstallation])

    def configureCommand(self):
        return 'cmake'

    def configureFlags(self):
        return [
            '-DCMAKE_INSTALL_PREFIX=$PREFIX',
            '-DENABLED_LOCAL_INFILE=ON',
            '-DMYSQL_UNIX_ADDR=$PREFIX/var/mysql/mysql.sock',
            '-DSYSCONFDIR=$SYSCONFDIR'
            '-DMYSQL_DATADIR=$PREFIX/var/mysql/'
            '-DINSTALL_INFODIR=$PREFIX/info',
            '-DWITH_SSL=no',
            '-DWITH_INNOBASE_STORAGE_ENGINE=1',
            '-DWITH_ARCHIVE_STORAGE_ENGINE=1',
            '-DWITH_BLACKHOLE_STORAGE_ENGINE=1',
            '-DWITH_PERFSCHEMA_STORAGE_ENGINE=1',
            '-DWITH_FEDERATED_STORAGE_ENGINE=1',
            '-DWITH_PARTITION_STORAGE_ENGINE=1',
            '-DCMAKE_OSX_DEPLOYMENT_TARGET=10.4',
            '-DINSTALL_LAYOUT=RPM'
        ]

    def completeInstallation(self, component, archs, builder):
        sandbox = Sandbox([self], builder)

        print("==> Complete MySQL installation")

        sandbox.setup()

        if not os.path.isdir(os.path.join(sandbox.path, 'etc')):
            os.makedirs(os.path.join(sandbox.path, 'etc'))

        # Install config file
        shutil.copy(
            os.path.join(self.resourcesPath, 'my.cnf'),
            os.path.join(sandbox.path, 'etc/my.cnf')
        )

        check_call([os.path.join(sandbox.path, "bin/mysql_install_db"), "--datadir=%s" % os.path.join(sandbox.path, "var/mysql/")])

        changes = sandbox.changes()

        print("Changes: %s", changes)

        filesToCopy = list(changes['new'])
        filesToCopy.extend([ file['file'] for file in changes['changed'] ])

        for src in filesToCopy:
            dest = os.path.join(self.buildPath, src[1:])

            if not os.path.isdir(os.path.dirname(dest)):
                os.makedirs(os.path.dirname(dest))

            shutil.copy(src, dest)

        sandbox.tearDown()
