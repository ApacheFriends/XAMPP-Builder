"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================

  The Builder class is the main class of the builder
  and coordinates everything that happen during the
  building of XAMPP.
"""
import os
from subprocess import check_call
from utils.file import isMachO

class FileUniversalizer(object):
    def applicableTo(self, path, arch_roots):
        raise NotImplemented()

    def universalizeFile(self, source, dest, arch_roots):
        raise NotImplemented()


class MachOUniversalizer(FileUniversalizer):
    def applicableTo(self, path, arch_roots):
        for arch, root in arch_roots.iteritems():
            if isMachO(os.path.join(root, path)) is None:
                return False

        return True

    def universalizeFile(self, source, dest, arch_roots):
        arch_flags = []

        for arch, root in arch_roots.iteritems():
            arch_flags.extend(['-arch', arch, os.path.join(root, source)])

        check_call(["lipo", "-create"] + arch_flags + ["-output", dest])