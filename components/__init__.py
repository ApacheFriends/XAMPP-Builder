"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

"""

import components.zlib.ZLib
import components.openssl.OpenSSL
import components.libjpeg.LibJPEG
import components.libltdl.LibLTDL
import components.libpng.LibPNG
import components.libungif.LibUnGIF
import components.libxml.LibXML
import components.libxslt.LibXSLT
import components.mcrypt.MCrypt
import components.mhash.MHash
import components.ncurses.Ncurses
import components.sqlite.SQLite
import components.expat.Expat
import components.freetds.FreeTDS
import components.freetype.FreeType
import components.gettext.Gettext
import components.apache.Apache
import components.mysql.MySQL
import components.proftpd.ProFTPd
import components.perl.Perl
import components.postgresql.Postgresql

KNOWN_COMPONENTS = [
	components.zlib.ZLib,
	components.openssl.OpenSSL,
	components.libjpeg.LibJPEG,
#	components.libltdl.LibLTDL,
	components.libpng.LibPNG,
	components.libungif.LibUnGIF,
	components.libxml.LibXML,
	components.libxslt.LibXSLT,
	components.mcrypt.MCrypt,
	components.mhash.MHash,
	components.ncurses.Ncurses,
	components.sqlite.SQLite,
	components.expat.Expat,
	components.freetds.FreeTDS,
	components.freetype.FreeType,
#	components.gettext.Gettext,
	components.apache.Apache,
	components.mysql.MySQL,
	components.proftpd.ProFTPd,
	components.perl.Perl,
#	components.postgresql.Postgresql
]