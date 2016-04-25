#!/usr/bin/env python

'''
pvWebMonitor.dev_main
'''

# Copyright (c) 2005-2016, UChicago Argonne, LLC.
# See LICENSE file for details.


import os
import sys
import time
import main
import setup


PROJECT_DIR = './www_project'


def setup_project_dir(path):
    '''(re)creates a project scratch directory'''
    path = os.path.abspath(path)
    
    # tear down any old directories
    if os.path.exists(path):
        for fname in os.listdir(path):
            os.remove(os.path.join(path, fname))
        os.rmdir(path)
        time.sleep(0.1)
    
    # tear down any old directories
    if not os.path.exists(path):
        os.mkdir(path)
        
    # fill it with the default files
    setup.main(path)


if __name__ == '__main__':
    '''start program with common code for developers'''
    #sys.argv.append('-h')
    #sys.argv.append('-v')
    sys.argv.append('config.xml')
    # - - - - - - - - -
    # this option is exclusive of the others
    #sys.argv.append('--setup')
    #sys.argv.append('./www')

    setup_project_dir(PROJECT_DIR)
    os.chdir(PROJECT_DIR)
    main.main()
