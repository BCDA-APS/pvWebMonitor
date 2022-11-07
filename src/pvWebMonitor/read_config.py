#!/usr/bin/env python

"""
Read XML configuration file for ``pvWebMonitor`` package.
"""

# Copyright (c) 2005-2020, UChicago Argonne, LLC.
# See LICENSE file for details.


from . import utils
from lxml import etree
import os


ROOT_TAG = "pvWebMonitor__config"
XML_SCHEMA_FILES = {
    "1.0": "config_1_0.xsd",
    "1.0.1": "config_1_0_1.xsd",
}
DEFAULT_FILE_UPLOAD_MATCH_PATTERNS = "*.html *.gif *.jpeg *.jpg *.png *.xsl".split()


def read_xml(xml_file):
    """
    return the configuration details as a dictionary

    :param return: dictionary

    the dictionary WILL contain these definitions for use by :meth:`pvwatch.PvWatch`:

    ========================  ===============  =================================================
    dictionary key            example (type)   description
    ========================  ===============  =================================================
    PVLIST_FILE               pvlist.xml       PVs to be monitored
    LOCAL_WWW_LIVEDATA_DIR    ./localwww       absolute path to local directory with "web site"
    LOG_INTERVAL_S            300 (float)      writing messages to log file
    REPORT_INTERVAL_S         10 (float)       updates to HTML pages
    SLEEP_INTERVAL_S          0.1 (float)      sleeps at end of main loop
    MAINLOOP_COUNTER_TRIGGER  10000 (int)      another logging message interval
    PATTERNS                  \*.html          upload all files that match these patterns
    ========================  ===============  =================================================

    """
    if not os.path.exists(xml_file):
        raise IOError(xml_file + " file not found")
    tree = etree.parse(xml_file)
    root = tree.getroot()
    schema_version = root.attrib["version"]

    utils.validate(tree, XML_SCHEMA_FILES[schema_version])

    root = tree.getroot()
    if root.tag != ROOT_TAG:
        msg = "XML root tag must be " + ROOT_TAG
        msg += ", found: " + root.tag
        raise ValueError(msg)

    pattern_handlers = {
        "1.0": patterns_1_0,
        "1.0.1": patterns_1_0_1,
    }
    conf = dict(
        PATTERNS=pattern_handlers[schema_version](tree), SCHEMA_VERSION=schema_version
    )

    for node in tree.findall(".//var"):
        key = node.get("name")
        value = node.get("value")
        data_type = node.get("type", "string").lower()
        if data_type in ("float", "int"):
            # represent number types as directed
            typeconversion = dict(float=float, int=int)[data_type]
            value = typeconversion(value)
        conf[key] = value

    return conf


def patterns_1_0(*args):
    """
    config_1_0 relies on a pre-defined list of file match patterns
    """
    return DEFAULT_FILE_UPLOAD_MATCH_PATTERNS


def patterns_1_0_1(*args):
    """
    config_1_0_1 uses a user-defined list of file match patterns
    """
    tree = args[0]
    return [node.get("value") for node in tree.findall(".//pattern")]
