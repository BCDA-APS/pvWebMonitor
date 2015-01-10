#!/usr/bin/env python

'''
pv2web_ro
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import datetime
import epics
import logging
from lxml import etree
import numpy
import os
import sys
import time
import traceback
import pv2web_ro


'''value for expected EPICS PV is None'''
class NoneEpicsValue(Exception): pass

'''pv not in pvdb'''
class PvNotRegistered(Exception): pass


class pvwatch(object):
    
    def __init__(self, configuration):
        self.configuration = configuration  # from XML configuration file
        self.pvdb = {}      # cache of last known good values
        self.xref = {}      # cross-reference between mnemonics and PV names: {mne:pvname}
        self.monitor_counter = 0

        self.get_pvlist()

        pv_conn = [pv['ch'].connected for pv in self.pvdb.values()]
        numConnected = numpy.count_nonzero(pv_conn)
        logMessage("Connected %d of total %d EPICS PVs" % (numConnected, len(self.pvdb)) )

    def start(self):
        '''begin receiving PV updates and posting new web content'''
        nextReport = getTime()
        nextLog = nextReport
        delta_report = datetime.timedelta(seconds=self.configuration['REPORT_INTERVAL_S'])
        delta_log = datetime.timedelta(seconds=self.configuration['LOG_INTERVAL_S'])
        mainLoopCount = 0

        while True:
            mainLoopCount = (mainLoopCount + 1) % self.configuration['MAINLOOP_COUNTER_TRIGGER']

            dt = getTime()
            epics.ca.poll()
        
            if mainLoopCount == 0:
                logMessage(" %s times through main loop" % self.configuration['MAINLOOP_COUNTER_TRIGGER'])
        
            if dt >= nextReport:
                nextReport = dt + delta_report
        
                try: self.report()                                   # write contents of pvdb to a file
                except Exception: logException("report()")
        
            if dt >= nextLog:
                nextLog = dt + delta_log
                msg = "checkpoint, %d EPICS monitor events received" % self.monitor_counter
                logMessage(msg)
                self.monitor_counter = 0  # reset

            time.sleep(self.configuration['SLEEP_INTERVAL_S'])
    
    def get_pvlist(self):
        '''get the PVs from the XML file'''
        pvlist_file = self.configuration['PVLIST_FILE']
        if not os.path.exists(pvlist_file):
            logMessage('could not find file: ' + pvlist_file)
            return
        try:
            tree = etree.parse(pvlist_file)
        except:
            logMessage('could not parse file: ' + pvlist_file)
            return

        for key in tree.findall(".//EPICS_PV"):
            if key.get("_ignore_", "false").lower() == "false":
                mne = key.get("mne")
                pv = key.get("PV")
                desc = key.get("description")
                fmt = key.get("display_format", "%s")  # default format
                try:
                    self.add_pv(mne, pv, desc, fmt)
                except:
                    msg = "%s: problem connecting: %s" % (pvlist_file, etree.tostring(key))
                    logException(msg)

    def add_pv(self, mne, pv, desc, fmt):
        '''Connect to a EPICS (PyEpics) process variable'''
        if pv in self.pvdb:
            msg = "key '%s' already defined by id=%s" % (pv, self.pvdb[pv]['id'])
            raise KeyError(msg)

        ch = epics.PV(pv)
        entry = {
            'name': pv,           # EPICS PV name
            'id': mne,            # symbolic name used in the python code
            'description': desc,  # text description for humans
            'timestamp': None,    # client time last monitor was received
            'counter': 0,         # number of monitor events received
            'units': "",          # engineering units
            'ch': ch,             # EPICS PV channel
            'format': fmt,        # format for display
            'value': None,        # formatted value
            'raw_value': None     # unformatted value
        }
        self.pvdb[pv] = entry
        self.xref[mne] = pv            # mne is local mnemonic, define actual PV in pvlist.xml
        ch.add_callback(self.EPICS_monitor_receiver)  # start callbacks now
        cv = ch.get_ctrlvars()
        unit_renames = {        # handle some non SI unit names
            # old      new
            'millime': 'mm',
            'millira': 'mr',
            'degrees': 'deg',
            'Volts':   'V',
            'VDC':     'V',
            'eng':     '',
        }
        if 'units' in cv:
            units = cv['units']
            if units in unit_renames:
                units = unit_renames[units]
            entry['units'] = units
        self.update_pvdb(pv, ch.get())   # initialize the cache

    def update_pvdb(self, pv, raw_value):
        if pv not in self.pvdb:
            msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
            raise PvNotRegistered, msg
        entry = self.pvdb[pv]
        # ch = entry['ch']
        entry['timestamp'] = getTime()
        entry['counter'] += 1
        entry['raw_value'] = raw_value
        entry['value'] = entry['format'] % raw_value

    def EPICS_monitor_receiver(self, *args, **kws):
        '''Response to an EPICS (PyEpics) monitor on the channel'''
        pv = kws['pvname']
        if pv not in self.pvdb:
            msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
            raise PvNotRegistered, msg
        self.update_pvdb(pv, kws['value'])   # cache the last known good value
        self.monitor_counter += 1

    def buildReport(self):
        '''build the report'''
        root = etree.Element("pv2web_ro")
        root.set("version", "1")
        node = etree.SubElement(root, "written_by")
        node.text = 'pv2web_ro/pvwatch'
        node = etree.SubElement(root, "datetime")
        node.text = str(getTime()).split('.')[0]
    
        sorted_id_list = sorted(self.xref)
        fields = ("name", "id", "description", "timestamp",
                  "counter", "units", "value", "raw_value", "format")
    
        for mne in sorted_id_list:
            pv = self.xref[mne]
            entry = self.pvdb[pv]
    
            node = etree.SubElement(root, "pv")
            node.set("id", mne)
            node.set("name", pv)
    
            for item in fields:
                subnode = etree.SubElement(node, item)
                subnode.text = str(entry[item])

        pi_xml = etree.ProcessingInstruction('xml', 'version="1.0"')
        pi_xsl = etree.ProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="pvlist.xsl"')
        xmlText = etree.tostring(pi_xml, pretty_print=True)
        xmlText += etree.tostring(pi_xsl, pretty_print=True)
        xmlText += etree.tostring(root, pretty_print=True)

        return xmlText

    def report(self):
        '''write the values out to files'''
    
        xmlText = self.buildReport()
    
        # WWW directory for livedata (absolute path)
        localDir = self.configuration['LOCAL_WWW_LIVEDATA_DIR']
    
        #--- write the XML with the raw data from EPICS
        raw_xml = self.configuration['XML_REPORT_FILE']
        abs_raw_xml = os.path.join(localDir, raw_xml)
        writeFile(abs_raw_xml, xmlText)
        copyToWebServer(abs_raw_xml, raw_xml)
    
        #--- xslt transforms from XML to HTML
    
        # make the index.html file
        index_html = self.configuration['HTML_INDEX_FILE']  # short name
        abs_index_html = os.path.join(localDir, index_html)  # absolute path
        xslt_transformation(self.configuration['LIVEDATA_XSL_STYLESHEET'], abs_raw_xml, abs_index_html)
        copyToWebServer(abs_index_html, index_html)  # copy to XSD
    
        # display the raw data (but pre-convert it in an html page)
        raw_html = self.configuration['HTML_RAWREPORT_FILE']
        abs_raw_html = os.path.join(localDir, raw_html)
        xslt_transformation(self.configuration['RAWTABLE_XSL_STYLESHEET'], abs_raw_xml, abs_raw_html)
        copyToWebServer(abs_raw_html, raw_html)
    
        # also copy the raw table XSLT
        xslFile = self.configuration['RAWTABLE_XSL_STYLESHEET']
        copyToWebServer(os.path.join(localDir, xslFile), xslFile)


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


def copyToWebServer(local_file, web_server_file):
    # scpToWebServer(os.path.join(localDir, xslFile), xslFile)
    pass


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
    watcher = pvwatch(configuration)
    watcher.start()


if __name__ == '__main__':
    '''simple test program for developers'''
    sys.argv.append('config.xml')
    #sys.argv.append('-h')
    #sys.argv.append('-v')
    main()
