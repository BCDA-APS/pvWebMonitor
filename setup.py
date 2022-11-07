#!/usr/bin/env python

# Copyright (c) 2005-2020, UChicago Argonne, LLC.
# See LICENSE file for details.


from setuptools import setup
import os
import sys
import versioneer

# pull in some definitions from the package's __init__.py file
sys.path.insert(
    0,
    os.path.join(
        "src",
    ),
)
import pvWebMonitor

requires = pvWebMonitor.__requires__
verbose = 1
long_description = open("README.rst", "r").read()


setup(
    name=pvWebMonitor.__package_name__,  # pvWebMonitor
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    license=pvWebMonitor.__license__,
    description=pvWebMonitor.__description__,
    long_description=long_description,
    author=pvWebMonitor.__author_name__,
    author_email=pvWebMonitor.__author_email__,
    url=pvWebMonitor.__url__,
    download_url=pvWebMonitor.__download_url__,
    keywords=pvWebMonitor.__keywords__,
    install_requires=requires,
    platforms="any",
    package_dir={"": "src"},
    packages=[
        str(pvWebMonitor.__package_name__),
    ],
    package_data={
        "pvWebMonitor": [
            "project/*",
            "*.xsd",
            "LICENSE",
            "VERSION",
        ]
    },
    classifiers=pvWebMonitor.__classifiers__,
    entry_points={
        # create & install console_scripts in <python>/bin
        "console_scripts": [
            "pvWebMonitor=pvWebMonitor.main:main",
        ],
        # 'gui_scripts': ['pvWebMonitor=pvWebMonitor.main:main'],
    },
)
