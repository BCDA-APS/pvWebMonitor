
'''
setup a new project directory
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import os
import sys


PROJECT_SOURCE_DIR = 'project'


def main(new_directory):
    '''
    setup a new project directory in *new_directory*
    
    *new_directory* must exist and not contain any of the files
    to be copied into it.
    
    :param str new_directory: name of existing directory
    '''
    if not os.path.exists(new_directory):
        raise RuntimeError('new project directory must exist: ' + new_directory)