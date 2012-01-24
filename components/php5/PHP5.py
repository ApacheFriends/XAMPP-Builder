"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The PHP5 component.
"""

from utils.Component import Component
from utils.Dependency import Dependency

from subprocess import check_call
import os.path

class PHP5(Component):

	def __init__(self, config):
		super(PHP5, self).__init__('PHP5', os.path.dirname(__file__), config)

		self.download_url = 'http://de2.php.net/distributions/php-%s.tar.gz' % self.version

		self.dependencies = [
			Dependency('Apache', configureFlags=["--with-apxs2=${PREFIX}/bin/apxs"]),
			Dependency('Ncurses', configureFlags=["--with-ncurses=${COMPONENT_PATH}"]),
			Dependency('LibJPEG', configureFlags=["--with-jpeg-dir=${COMPONENT_PATH}"]),
			Dependency('LibPNG', configureFlags=["--with-png-dir=${COMPONENT_PATH}"]),
			Dependency('FreeType', configureFlags=["--with-freetype-dir=${COMPONENT_PATH}"]),
			Dependency('ZLib', configureFlags=["--with-zlib=shared", "--with-zlib-dir=${COMPONENT_PATH}"]),
			Dependency('OpenSSL', configureFlags=["--with-openssl=${COMPONENT_PATH}"]),
			Dependency('Expat', configureFlags=["--with-expat-dir=${COMPONENT_PATH}"]),
			Dependency('LibXSLT', configureFlags=["--with-xsl=shared,${COMPONENT_PATH}"]),
			Dependency('MCrypt', configureFlags=["--with-mcrypt=${COMPONENT_PATH}"]),
			Dependency('MHash', configureFlags=["--with-mhash=${COMPONENT_PATH}"]),
			Dependency('LibXML', configureFlags=["--with-libxml-dir=${COMPONENT_PATH}"]),
			Dependency('FreeTDS', configureFlags=["--with-mssql=${COMPONENT_PATH}", "--with-pdo-mssql=shared,${COMPONENT_PATH}"]),
			Dependency('MySQL', configureFlags=[
				"--with-mysql=${COMPONENT_PATH}", 
				"--with-mysql-sock=$PREFIX/var/mysql/mysql.sock",
				"--with-pdo-mysql=shared,${COMPONENT_PATH}/bin/mysql_config",
				"--with-mysql=shared,${COMPONENT_PATH}",
				"--with-mysqli=shared,${COMPONENT_PATH}/bin/mysql_config"
				])
		]
		
		self.patches = [
			'php5_config.patch',
			'php5_uni.patch',
			'apxs-install.patch' # Redhat bug 181798, this also requires autoconf --force
		]
		
		self.buildSteps.insert(self.buildSteps.index("configure"), self.runAutoconf)
		self.buildSteps.insert(self.buildSteps.index("configure"), "setupSandbox")
		self.buildSteps.insert(self.buildSteps.index("install") + 1, "tearDownSandbox")

	def configureFlags(self):
		flags = super(PHP5, self).configureFlags()

		flags.extend([
			# Support for multiple php versions
			'--program-suffix=-%s' % self.version,
			'--libdir=$PREFIX/lib/php/php-%s' % self.version,
			'--includedir=$PREFIX/include/php/php-%s' % self.version,
			
			# Otherwise will hang on /ext/fileinfo/libmagic/apprentice.c
			'--disable-fileinfo',
			
			'--with-config-file-path=$SYSCONFDIR',
			
			'--disable-debug',
			'--enable-cli',
			'--enable-cgi',
			'--enable-bcmath',
			'--enable-calendar',
			'--enable-ctype',
			'--enable-discard-path',
			'--enable-filepro',
			'--enable-filter',
			'--enable-force-cgi-redirect',
			'--enable-fastcgi',
			'--enable-ftp',
			'--enable-hash',
			'--enable-ipv6',
			'--enable-json',
			'--enable-odbc',
			'--enable-path-info-check',
			'--enable-gd-imgstrttf',
			'--enable-gd-native-ttf',
			'--with-ttf',
			'--enable-magic-quotes',
			'--enable-memory-limit',
			'--enable-safe-mode',
			'--enable-shmop',
			'--enable-sysvsem',
			'--enable-sysvshm',
			'--enable-track-vars',
			'--enable-trans-sid',
			'--enable-reflection',
			'--enable-session',
			'--enable-spl',
			'--enable-tokenizer',
			'--enable-wddx',
			'--enable-yp',
			'--enable-xmlreader',
			'--enable-xmlwriter',
			'--enable-zlib',
			'--enable-zts',
			'--with-simplexml',
			'--with-iconv',
			'--with-libxml',
			'--with-wddx',
			'--with-xml',
			'--with-ftp',
			
			# '--with-gdbm=$PREFIX',

			'--without-xpm',
			
			# Need this? '--enable-xslt=shared,$PREFIX',
			# Need this? '--with-dom=shared,$PREFIX',
			
			# '--with-ldap=shared,$PREFIX',
			'--with-gd=shared',
			
			
			'--enable-sockets',
			'--enable-zend-multibyte',
			
			'--enable-pcntl',
			'--enable-dbx=shared',
			
			'--with-pear=$PREFIX/lib/php/pear',
#			'--with-imap-dir=$PREFIX',
#			'--with-imap=shared,$PREFIX',
			'--enable-mbstring=shared,all',
			
			# Broken '--with-gettext=$PREFIX',
			'--enable-apache2-2filter=shared',
			'--enable-apache2-2handler=shared',
			'--with-bz2=shared',
			'--with-curl=shared',
			'--with-dba=shared',
			'--enable-dbase=shared',
			'--with-fdf=shared',
			'--enable-mbregex',
			'--enable-mbregex-backtrack',
			'--with-mime-magic=shared',
			
			'--enable-shmop=shared',
			'--with-snmp=shared',
			'--enable-sockets=shared',
			'--enable-pdo',
			
			'--enable-zip=shared,$PREFIX',
			'--enable-exif=shared',
			
			
			
			
			'--enable-soap=shared',
			'--with-xmlrpc=shared',
			'--with-oracle=shared',
			'--with-pdf=shared',
			'--with-sqlite3=shared,$PREFIX',
			
			# MySQL
			
			
			# Postgre
			# '--with-pgsql=shared,$PREFIX',
			# '--with-pdo-pgsql=shared,$PREFIX',
			
			# SQLITE
			'--with-sqlite=shared',
			'--with-pdo-sqlite=shared',
			'--with-pdo-sqlite-external=shared',

		])

		return  flags

	def installFlags(self):
		return [
			"install",
			"INSTALL_ROOT=${DEST_DIR}"
		]
	
	def runAutoconf(self, component, archs, builder):
		check_call(["autoconf", "--force"])

