

'''
pv2web_ro.utils
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import datetime
import logging
from lxml import etree
import os
import sys
import traceback


def copyToWebServer(local_file, web_server_file):
    '''placeholder in case a more advanced copy method is needed'''
    # scpToWebServer(os.path.join(localDir, xslFile), xslFile)
    pass


def getTime():
    '''simple wrapper for common timenow() function'''
    return datetime.datetime.now()


def logMessage(message):
    '''
    log a message or report from pv2web_ro

    :param str message: words to be logged
    '''
    now = getTime()
    name = os.path.basename(sys.argv[0])
    pid = os.getpid()
    text = "(%d,%s,%s) %s" % (pid, name, now, message)
    logging.info(text)


def logException(troublemaker):
    '''
    write an exception report to the log file

    :param obj troublemaker: instance of Exception
    '''
    msg = "problem with %s:" % troublemaker
    for _ in msg.splitlines():
        logMessage(_)
    for _ in traceback.format_exc().splitlines():
        logMessage('\t' + _)


def validate(xml_tree, xml_schema_file):
    '''
    validate an XML document tree against an XML Schema file

    :param obj xml_tree: instance of etree._ElementTree
    :param str xml_schema_file: name of XML Schema file (local to package directory)
    '''
    path = os.path.abspath(os.path.dirname(__file__))
    xsd_file_name = os.path.join(path, xml_schema_file)
    if not os.path.exists(xsd_file_name):
        raise IOError('Could not find XML Schema file: ' + xml_schema_file)
    
    xsd_doc = etree.parse(xsd_file_name)
    xsd = etree.XMLSchema(xsd_doc)

    return xsd.assertValid(xml_tree)


def writeFile(output_file, contents):
    '''
    write contents to file

    :param str output_file: file to be written (path is optional)
    :param str contents: text to write in *output_file*
    '''
    f = open(output_file, 'w')
    f.write(contents)
    f.close()


def xslt_transformation(xslt_file, src_xml_file, result_xml_file):
    '''
    transform an XML file using an XSLT

    :param str xslt_file: name of XSLT file
    :param str src_xml_file: name of XML file
    :param str result_xml_file: name of output XML file
    '''
    src_doc = etree.parse(src_xml_file)
    xslt_doc = etree.parse(xslt_file)
    transform = etree.XSLT(xslt_doc)
    result_doc = transform(src_doc)
    buf = etree.tostring(result_doc, pretty_print=True)
    writeFile(result_xml_file, buf)
