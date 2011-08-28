"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Apache component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

import os.path

class Apache(Component):

    def __init__(self, config):
        super(Apache, self).__init__('Apache', os.path.dirname(__file__), config)

        self.download_url = 'http://mirror.checkdomain.de/apache/httpd/httpd-%s.tar.gz' % self.version

        self.dependencies = [
            Dependency('ZLib', configureFlags=["--with-z=${COMPONENT_PATH}"]),
            Dependency('Expat', configureFlags=["--with-expat=${COMPONENT_PATH}"]),
            Dependency('OpenSSL', configureFlags=["--with-ssl=${COMPONENT_PATH}", "--enable-ssl=shared,${COMPONENT_PATH}"])
        ]

        self.patches = [
            'rm_envvars.patch',
            'ulimit_fix.patch'
        ]

    def configureFlags(self):
        flags = super(Apache, self).configureFlags()

        flags.extend([
            '--enable-nonportable-atomics',
            '--enable-so',
            '--enable-cgid',
            '--enable-auth-anon',
            '--enable-auth-dbm',
            '--enable-auth-digest',
            '--enable-file-cache',
            '--enable-echo',
            '--enable-charset-lite',
            '--enable-cache',
            '--enable-disk-cache',
            '--enable-mem-cache',
            '--enable-ext-filter',
            '--enable-case-filter',
            '--enable-case-filter-in',
            '--enable-deflate',
            '--enable-mime-magic',
            '--enable-cern-meta',
            '--enable-expires',
            '--enable-headers',
            '--enable-usertrack',
            '--enable-unique-id',
            '--enable-proxy',
            '--enable-proxy-connect',
            '--enable-proxy-ftp',
            '--enable-proxy-http',
            '--enable-bucketeer',
            '--enable-http',
            '--enable-info',
            '--enable-suexec',
            '--enable-cgid',
            '--enable-vhost-alias',
            '--enable-speling',
            '--enable-rewrite',
            '--enable-so',
            '--enable-dav',
            '--enable-dav-fs',
            '--enable-mods-shared=most',
            '--with-mpm=prefork',
            '--with-suexec-caller=nobody',
            '--with-suexec-docroot=/Applications/XAMPP/htdocs',
            '--without-berkeley-db',
            '--without-pgsql',
            '--enable-ipv6',
            '--with-included-apr',
            '--without-ldap',
            '--disable-ldap'
        ])

        return  flags

