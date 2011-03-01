'''
  XAMPP Builder
  Copyright 2011 Apache Friends, GPLv2+ licensed
  ==============================================
'''

import os.path

def isMachO(file):
    (path, ext) = os.path.splitext(file)
    
    '''
      It's a java class file and no mach-o file.
      This special case is because java class files
      have the same magic number as fat-binaries.
    '''
    
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
