

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
    # scpToWebServer(os.path.join(localDir, xslFile), xslFile)
    pass


def getTime():
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
    '''write an exception report to the log file'''
    msg = "problem with %s:" % troublemaker
    for _ in msg.splitlines():
        logMessage(_)
    for _ in traceback.format_exc().splitlines():
        logMessage('\t' + _)


def writeFile(output_file, contents):
    '''write contents to file'''
    f = open(output_file, 'w')
    f.write(contents)
    f.close()


def xslt_transformation(xslt_file, src_xml_file, result_xml_file):
    '''transform an XML file using an XSLT'''
    src_doc = etree.parse(src_xml_file)
    xslt_doc = etree.parse(xslt_file)
    transform = etree.XSLT(xslt_doc)
    result_doc = transform(src_doc)
    buf = etree.tostring(result_doc, pretty_print=True)
    writeFile(result_xml_file, buf)
