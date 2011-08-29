"""
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================
"""
import gzip
import hashlib
import os
import os.path
import shutil

def isMachO(file):
    (path, ext) = os.path.splitext(file)
    
    # It's a java class file and no mach-o file. This special case is because java class files have the same magic
    # number as fat-binaries.
    if ext == '.class':
        return False

    with open(file, 'rb') as f:
        magic = f.read(4)
        
        if (magic == '\xca\xfe\xba\xbe' or # fat-binary magic number
            magic == '\xfe\xed\xfa\xce' or # mach-o binary magic number
            magic == '\xce\xfa\xed\xfe'):  # mach-o binary magic number (reverse endianiss)
            return True     
        else:
            return False
    
def isAr(file):
    with open(file, 'rb') as f:
        magic = f.read(8)
        
        if magic == '!<arch>\x0a':  # ar binary magic string
            return True     
        else:
            return False

def hashForFile(file):
    """
     Returns an usefull hash for comparisions.

     - Links will be hashed as link and not as the file they're pointing to.
     - Compressed files will hashed uncompressed
    """
    hash = hashlib.sha1()
    (root, ext) = os.path.splitext(file)
    if os.path.islink(file):
        hash.update(os.readlink(file))
    elif ext == '.gz':
        f = gzip.open(file, 'rb')
        for data in f.read(512):
            hash.update(data)
        f.close()
    else:
        with open(file, 'rb') as f:
            for data in f.read(512):
                hash.update(data)
    return hash.hexdigest()

def digestsInPath(path, relative=True):
    """
     Calculate an hash for every file under an given path.
    """

    result = {}

    if not os.path.isdir(path):
        raise StandardError('path "%s" is not a directory' % path)

    for root, dirs, files in os.walk(path):
        for file in files:
            rel_path = os.path.join(root, file)
            digest = hashForFile(rel_path)
            if relative:
                rel_path = os.path.relpath(rel_path, path)
            result[rel_path] = digest

    return result

def copytree(src, dst, symlinks=False, ignore=None):
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.exists(dst):
        os.makedirs(dst)
    elif not os.path.isdir(dst):
        raise StandardError('%s has to be a directory!' % dst)

    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                copytree(srcname, dstname, symlinks, ignore)
            else:
                shutil.copy2(srcname, dstname)
            # XXX What about devices, sockets etc.?
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive my_copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except shutil.WindowsError:
        # can't copy file access times on Windows
        pass
    except OSError, why:
        errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error(errors)
