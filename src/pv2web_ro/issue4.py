

'''
pv2web_ro.pvwatch
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import fnmatch
import os

import read_config
import utils

XML_RAWDATA_FILE_NAME = 'rawdata.xml'
XSL_PVLIST_FILE_NAME = 'pvlist.xsl'
XSL_RAWDATA_FILE_NAME = 'rawdata.xsl'
XSL_INDEX_FILE_NAME = 'index.xsl'
UPLOAD_FILE_EXTENSION_MATCHES = ('*.html', '*.gif', '*.jpeg', '*.jpg', '*.png', '*.xsl')


def _xslt_(xslt_file, source_xml_file):
    '''convenience routine for long name'''
    output_xml_file = os.path.splitext(xslt_file)[0] + os.extsep + 'html'
    utils.xslt_transformation(xslt_file, source_xml_file, output_xml_file)


def report(cfg):
    '''
    write the values out to files
    
    The values of the monitored EPICS PVs (the "raw data")
    is written to an XML file.  This file is then used
    with one or more XSLT stylesheets to create HTML pages.
    An overall "home page" (index.html) is created to provide
    a table of contents of this static web site.
    
    :param dict cfg: program configuration dictionary
    '''
    
    # accumulate list of each file written below
    www_site_file_list = []
    xslt_file_list_used = ['index.xsl', ]  # do the index.xsl file last

    # add pvlist.xml to file list
    pvlist_xml_file_name = cfg['PVLIST_FILE']
    www_site_file_list.append(pvlist_xml_file_name)
    
    # add pvlist.xsl to file list
    xslt_file_name = XSL_PVLIST_FILE_NAME
    if os.path.exists(xslt_file_name):
        _xslt_(xslt_file_name, pvlist_xml_file_name)
        xslt_file_list_used.append(xslt_file_name)

    # add report.xml to file list
    report_xml_file_name = XML_RAWDATA_FILE_NAME
    if os.path.exists(report_xml_file_name):
        # write "report.xml"    : values of monitored EPICS PVs
        www_site_file_list.append(report_xml_file_name)
        
        xslt_file_name = XSL_RAWDATA_FILE_NAME
        if os.path.exists(xslt_file_name):
            _xslt_(xslt_file_name, report_xml_file_name)
            xslt_file_list_used.append(xslt_file_name)

            # convert all .xsl files
            xslt_files = fnmatch.filter(os.listdir('.'), '*.xsl')
            for xslt_file_name in xslt_files:
                if xslt_file_name not in xslt_file_list_used:
                    _xslt_(xslt_file_name, report_xml_file_name)

    # finally, write index.html from file list, table of files and descriptions as provided
    xslt_file_name = XSL_INDEX_FILE_NAME
    if os.path.exists(xslt_file_name):
        # TODO: each XSLT file has a "description" attribute
        #  This could be used when building "index.html" file
        #  For now, this is manually copied from .xsl file to the table in index.xsl
        #  To automate this process, a new, temporary XML document will need to be
        #  created with the names and descriptions of all HTML pages.
        #  Then use that XML in the following XSLT.
        #  Also should add a time stamp string.
        _xslt_(xslt_file_name, report_xml_file_name)
    
    # include any other useful files from the project directory
    local_files = os.listdir('.')
    for extension_match in UPLOAD_FILE_EXTENSION_MATCHES:
        www_site_file_list += fnmatch.filter(local_files, extension_match)
        www_site_file_list += fnmatch.filter(local_files, extension_match.upper())
    
    # only copy files if web_site_path is not the current dir
    www_site_file_list = sorted(set(www_site_file_list))
    www_site_path = os.path.abspath(cfg['LOCAL_WWW_LIVEDATA_DIR'])
    if www_site_path != os.path.abspath(os.getcwd()):
        for fname in www_site_file_list:
            utils.copyToWebServer(fname, www_site_path)


# --------------------------------------------------

os.chdir('www_project')
cfg = read_config.read_xml('config.xml')
report(cfg)
