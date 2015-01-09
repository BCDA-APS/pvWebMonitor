#!/usr/bin/env python

'''
read XML configuration file for `pv2web_ro` package
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import os
from lxml import etree


ROOT_TAG = 'pv2web_ro__config'


def read_xml(xml_file):
    '''return the configuration details as a dictionary'''
    if not os.path.exists(xml_file):
        raise IOError(xml_file + ' file not found')
    tree = etree.parse(xml_file)
    root = tree.getroot()
    if root.tag != ROOT_TAG:
        msg = 'XML root tag must be ' + ROOT_TAG
        msg += ', found: ' + root.tag
        raise ValueError(msg)
    
    conf = {}
    for node in root:
        key = node.tag
        value = node.get('value')
        data_type = node.get('type', 'string').lower()
        if data_type in ( 'float', 'int' ):
            # represent number types as directed
            typeconversion = dict(float=float, int=int)[data_type]
            value = typeconversion(value)
        conf[key] = value
        
    return conf
