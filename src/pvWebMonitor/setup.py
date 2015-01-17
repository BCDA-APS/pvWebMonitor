
'''
setup a new project directory
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import os


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
    
    src_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), PROJECT_SOURCE_DIR)
    src_files = os.listdir(src_path)
    new_files = os.listdir(new_directory)
    
    if _ok_to_proceed_(src_files, new_files):
        import shutil
        for fname in src_files:
            # TODO: configure each file for local machine
            src = os.path.join(src_path, fname)
            dest = os.path.join(new_directory, fname)
            shutil.copyfile(src, dest)
    else:
        raise RuntimeError('new project directory contains files that would be overwritten: ' + new_directory)


def _ok_to_proceed_(src_files, new_files):
    '''
    not ok if any src_files are in new_files list
    
    :param [str] src_files: list of file names in source directory
    :param [str] new_files: list of file names in new directory
    '''
    if len(new_files) == 0: return True
    for fname in new_files:
        if fname in src_files:
            return False
    return True
