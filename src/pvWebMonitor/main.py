#!/usr/bin/env python

"""
pvWebMonitor.main

USAGE::

    ~$ pvWebMonitor
    usage: pvWebMonitor [-h] [-l LOG_FILE] [-v] xml_config_file
    pvWebMonitor: error: too few arguments

HELP::

    ~$ pvWebMonitor -h
    usage: pvWebMonitor [-h] [-l LOG_FILE] [-v] [--setup SETUP] xml_config_file

    pvWebMonitor: post EPICS PVs to read-only web page

    positional arguments:
      xml_config_file       XML configuration file

    optional arguments:
      -h, --help            show this help message and exit
      -l LOG_FILE, --log_file LOG_FILE
                            log file
      -v, --version         show program's version number and exit

    getting started (none of the above):
      --setup SETUP         setup a new project directory

VERSION::

    ~$ pvWebMonitor -v
    2015.0112.0

"""


import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
DEFAULT_LOG_FILE = "log_file.txt"


def main():
    """entry point for the command-line interface"""
    import argparse

    from . import __package_name__
    from . import __version__
    from . import read_config

    doc = f"{__package_name__}: Create static web site from EPICS PVs."

    parser = argparse.ArgumentParser(description=doc)

    if "--setup" not in sys.argv:
        parser.add_argument(
            "xml_config_file",
            action="store",
            help="XML configuration file",
            default="configuration.xml",
        )

        parser.add_argument("-l", "--log_file", action="store", help="log file", default="log_file.txt")

        parser.add_argument("-v", "--version", action="version", version=__version__)

    group = parser.add_argument_group("getting started (none of the above)")
    group.add_argument("--setup", help="setup a new project directory", type=str)

    user_args = parser.parse_args()

    try:
        log_file = user_args.log_file
    except AttributeError:
        log_file = DEFAULT_LOG_FILE
    logging.basicConfig(filename=log_file, level=logging.INFO)

    if user_args.setup is not None:
        logger.info("Setup requested in directory: %s", user_args.setup)
        from . import setup

        setup.main(user_args.setup)
        exit()

    else:
        from . import pvwatch

        logger.debug("-" * 40)
        logger.info("pvWebMonitor starting")
        configuration = read_config.read_xml(user_args.xml_config_file)
        logger.debug("read configuration file: %s", user_args.xml_config_file)
        logger.debug(
            "configuration schema version: %s",
            configuration["SCHEMA_VERSION"],
        )

        watcher = pvwatch.PvWatch(configuration)

        logger.debug("starting the monitor and report cycle")
        watcher.start()


# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2005-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
