#!/usr/bin/env python

"""
pvWebMonitor.dev_main
"""

# Copyright (c) 2005-2022, University of Chicago, The Regents of the University of California, and Berliner Elektronenspeicherring Gesellschaft fuer Synchrotronstrahlung m.b.H. (BESSY) All rights reserved.
# See LICENSE file for details.


import logging
import pathlib
import sys
import time

import setup
from pvWebMonitor import main

logging.basicConfig(level="DEBUG")
logging.getLogger("ophyd").setLevel("WARNING")
PROJECT_DIR = "./www_project"


def setup_project_dir(path):
    """(re)creates a project scratch directory"""
    path = pathlib.Path(path)

    # tear down any old directories
    if path.exists():
        for fname in path.iterdir():
            fname.unlink()
        path.rmdir()
        time.sleep(0.1)

    # tear down any old directories
    if not path.exists():
        path.mkdir()

    # fill it with the default files
    setup.main(path)


if __name__ == "__main__":
    """start program with common code for developers"""
    # sys.argv.append('-h')
    # sys.argv.append('-v')
    sys.argv.append("config.xml")
    # - - - - - - - - -
    # this option is exclusive of the others
    # sys.argv.append('--setup')
    # sys.argv.append('./www')

    setup_project_dir(PROJECT_DIR)
    pathlib.os.chdir(PROJECT_DIR)
    main.main()
