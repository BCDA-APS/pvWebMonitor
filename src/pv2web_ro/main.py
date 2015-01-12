#!/usr/bin/env python

'''
pv2web_ro.main
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import logging
import sys

import pv2web_ro
import pvwatch
import utils


def main():
    import argparse
    import read_config
    
    doc = pv2web_ro.__package_name__
    doc += ': ' + pv2web_ro.__description__
    parser = argparse.ArgumentParser(description=doc)

    parser.add_argument('xml_config_file', 
                        action='store', 
                        help="XML configuration file",
                        default='configuration.xml')

    parser.add_argument('-l', '--log_file', 
                        action='store', 
                        help="log file",
                        default='log_file.txt')

    parser.add_argument('-v', '--version', action='version', version=pv2web_ro.__version__)

    user_args = parser.parse_args()
    
    logging.basicConfig(filename=user_args.log_file, level=logging.INFO)

    configuration = read_config.read_xml(user_args.xml_config_file)
    utils.logMessage('read configuration file: ' + user_args.xml_config_file)

    watcher = pvwatch.PvWatch(configuration)

    utils.logMessage('starting the monitor and report cycle')
    watcher.start()


if __name__ == '__main__':
    '''simple test program for developers'''
    sys.argv.append('config.xml')
    #sys.argv.append('-h')
    #sys.argv.append('-v')
    main()
