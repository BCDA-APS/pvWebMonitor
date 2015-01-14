#!/usr/bin/env python

'''
pv2web_ro.dev_main
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import os
import sys
import main


if __name__ == '__main__':
    '''start program with common code for developers'''
    #sys.argv.append('-h')
    #sys.argv.append('-v')
    #sys.argv.append('config.xml')
    # - - - - - - - - -
    # this option is exclusive of the others
    sys.argv.append('--setup')
    sys.argv.append('./www')
    main.main()
