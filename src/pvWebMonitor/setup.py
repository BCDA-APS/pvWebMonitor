'''
setup a new project directory
'''

# Copyright (c) 2005-2016, UChicago Argonne, LLC.
# See LICENSE file for details.


import os
import sys
import platform
import stat


PROJECT_SOURCE_DIR = 'project'


def get_key_value(key, txt):
    '''
    find the assignment line in txt: key=value, and return value
    '''
    separator = '='
    pattern = key + separator
    sub = [_ for _ in txt.splitlines() if pattern in _ and _.startswith(key)]
    if len(sub) != 1:
        raise KeyError('could not unique find key=' + key)
    return sub[0].split(separator)[1]
    

def modify_manage_script(filename):
    '''
    customize the manage.sh script for the current setup
    '''
    if not os.path.exists(filename): return

    manage_sh = open(filename, 'r').read()

    old_path = get_key_value('PROJECT_DIR', manage_sh)
    old_executable_script = get_key_value('EXECUTABLE_SCRIPT', manage_sh)
    
    path = os.path.abspath(os.path.dirname(filename))
    executable_script = os.path.abspath(sys.argv[0])

    manage_sh = manage_sh.replace(old_path, path)
    manage_sh = manage_sh.replace(old_executable_script, executable_script)
    
    with open(filename, 'w') as f:
        f.write(manage_sh)
    if platform.system() in ('Linux',):     # TODO: What about Mac, other *NIX?
        permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
        permissions |= stat.S_IRGRP | stat.S_IXGRP
        permissions |= stat.S_IROTH | stat.S_IXOTH
        os.chmod(filename, permissions)


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
    
    if not _ok_to_proceed_(src_files, new_files):
        msg = 'new project directory contains files that would be overwritten: '
        raise RuntimeError(msg + new_directory)

    import shutil
    for fname in src_files:
        src = os.path.join(src_path, fname)
        dest = os.path.join(new_directory, fname)
        shutil.copyfile(src, dest)
    
    # customize the manage.sh script to the current setup
    owd = os.getcwd()
    os.chdir(new_directory)
    modify_manage_script('manage.sh')
    os.chdir(owd)


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
