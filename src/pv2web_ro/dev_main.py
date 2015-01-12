#!/usr/bin/env python

'''
pv2web_ro.dev_main
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import sys
import main


if __name__ == '__main__':
    '''start program with common code for developers'''
    sys.argv.append('config.xml')
    #sys.argv.append('-h')
    #sys.argv.append('-v')
    main.main()
