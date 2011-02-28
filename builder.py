#!/usr/bin/python

'''
 XAMPP Builder
 Copyright 2011 Apache Friends, GPLv2+ licensed
 ==============================================

 This is an little helper file which setups the
 enviroment and then starts the Builder.
'''

import sys
import os.path

''' Add the dir of this file to the PATH to get utils and components to include '''
sys.path.append(os.path.dirname(__file__))

from utils.Builder import Builder

if __name__ == '__main__':
    ''' Start the builder '''
    Builder().run()
