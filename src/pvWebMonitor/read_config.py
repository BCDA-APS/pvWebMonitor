#!/usr/bin/env python

'''
read XML configuration file for `pvWebMonitor` package
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import os
from lxml import etree
import utils


ROOT_TAG = 'pvWebMonitor__config'
XML_SCHEMA_FILE = 'config.xsd'


def read_xml(xml_file):
    '''
    return the configuration details as a dictionary
    
    :param return: dictionary
    
    At minimum, the dictionary should contain these definitions for use by :meth:`pvwatch.PvWatch`:
    
    ========================  ===============  =================================================
    dictionary key            example (type)   description
    ========================  ===============  =================================================
    PVLIST_FILE               pvlist.xml       PVs to be monitored
    LOCAL_WWW_LIVEDATA_DIR    ./localwww       absolute path to local directory with "web site"
    LOG_INTERVAL_S            300 (float)      writing messages to log file
    REPORT_INTERVAL_S         10 (float)       updates to HTML pages
    SLEEP_INTERVAL_S          0.1 (float)      sleeps at end of main loop
    MAINLOOP_COUNTER_TRIGGER  10000 (int)      another logging message interval
    ========================  ===============  =================================================

    '''
    if not os.path.exists(xml_file):
        raise IOError(xml_file + ' file not found')
    tree = etree.parse(xml_file)
    
    utils.validate(tree, XML_SCHEMA_FILE)
    
    root = tree.getroot()
    if root.tag != ROOT_TAG:
        msg = 'XML root tag must be ' + ROOT_TAG
        msg += ', found: ' + root.tag
        raise ValueError(msg)
    
    conf = {}
    for node in tree.findall(".//var"):
        key = node.get('name')
        value = node.get('value')
        data_type = node.get('type', 'string').lower()
        if data_type in ( 'float', 'int' ):
            # represent number types as directed
            typeconversion = dict(float=float, int=int)[data_type]
            value = typeconversion(value)
        conf[key] = value
        
    return conf
