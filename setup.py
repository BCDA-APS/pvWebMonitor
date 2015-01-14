#!/usr/bin/env python

# Copyright (c) 2009 - 2014, UChicago Argonne, LLC.
# See LICENSE file for details.


from setuptools import setup, find_packages
import os
import re
import sys

# pull in some definitions from the package's __init__.py file
sys.path.insert(0, os.path.join('src', ))
import pv2web_ro

requires = pv2web_ro.__requires__
packages = find_packages()
verbose=1
long_description = open('README.rst', 'r').read()


setup (name             = pv2web_ro.__package_name__,        # pv2web_ro
       version          = pv2web_ro.__version__,
       license          = pv2web_ro.__license__,
       description      = pv2web_ro.__description__,
       long_description = long_description,
       author           = pv2web_ro.__author_name__,
       author_email     = pv2web_ro.__author_email__,
       url              = pv2web_ro.__url__,
       download_url     = pv2web_ro.__download_url__,
       keywords         = pv2web_ro.__keywords__,
       install_requires = requires,
       platforms        = 'any',
       package_dir      = {'pv2web_ro': 'src/pv2web_ro'},
       #packages         = find_packages(),
       packages         = [str(pv2web_ro.__package_name__), ],
       package_data     = {'pv2web_ro': ['project/*']},
       classifiers      = pv2web_ro.__classifiers__,
       entry_points={
          # create & install console_scripts in <python>/bin
          'console_scripts': [
            'pv2web_ro=pv2web_ro.main:main', 
          ],
          #'gui_scripts': ['pv2web_ro=pv2web_ro.main:main'],
      },
  )
