

'''
pv2web_ro.pvwatch
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import datetime
import epics
from lxml import etree
import numpy
import os
import time
import utils


'''pv not in pvdb'''
class PvNotRegistered(Exception): pass

'''Could not parse XML file'''
class CouldNotParseXml(Exception): pass


class PvWatch(object):
    
    def __init__(self, configuration):
        self.configuration = configuration  # from XML configuration file
        self.pvdb = {}      # cache of last known good values
        self.xref = {}      # cross-reference between mnemonics and PV names: {mne:pvname}
        self.monitor_counter = 0

        self.get_pvlist()
        utils.logMessage('read list of PVs to monitor')

        pv_conn = [pv['ch'].connected for pv in self.pvdb.values()]
        numConnected = numpy.count_nonzero(pv_conn)
        utils.logMessage("Connected %d of total %d EPICS PVs" % (numConnected, len(self.pvdb)) )

    def start(self):
        '''begin receiving PV updates and posting new web content'''
        nextReport = utils.getTime()
        nextLog = nextReport
        delta_report = datetime.timedelta(seconds=self.configuration['REPORT_INTERVAL_S'])
        delta_log = datetime.timedelta(seconds=self.configuration['LOG_INTERVAL_S'])
        mainLoopCount = 0

        while True:
            mainLoopCount = (mainLoopCount + 1) % self.configuration['MAINLOOP_COUNTER_TRIGGER']

            dt = utils.getTime()
            epics.ca.poll()
        
            if mainLoopCount == 0:
                utils.logMessage(" %s times through main loop" % self.configuration['MAINLOOP_COUNTER_TRIGGER'])
        
            if dt >= nextReport:
                nextReport = dt + delta_report
        
                try: self.report()                                   # write contents of pvdb to a file
                except Exception: utils.logException("report()")
        
            if dt >= nextLog:
                nextLog = dt + delta_log
                msg = "checkpoint, %d EPICS monitor events received" % self.monitor_counter
                utils.logMessage(msg)
                self.monitor_counter = 0  # reset

            time.sleep(self.configuration['SLEEP_INTERVAL_S'])
    
    def get_pvlist(self):
        '''get the PVs from the XML file'''
        pvlist_file = self.configuration['PVLIST_FILE']
        if not os.path.exists(pvlist_file):
            utils.logMessage('could not find file: ' + pvlist_file)
            return
        try:
            tree = etree.parse(pvlist_file)
        except:
            msg = 'could not parse file: ' + pvlist_file
            utils.logMessage(msg)
            raise CouldNotParseXml(msg)

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
                    utils.logException(msg)

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
        if cv is not None and 'units' in cv:
            units = cv['units']
            if units in unit_renames:
                units = unit_renames[units]
            entry['units'] = units
        # FIXME: what to do if PV did not connect? (ch.connected == False)
        self.update_pvdb(pv, ch.get())   # initialize the cache

    def update_pvdb(self, pv, raw_value):
        if pv not in self.pvdb:
            msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
            raise PvNotRegistered, msg
        entry = self.pvdb[pv]
        # ch = entry['ch']
        entry['timestamp'] = utils.getTime()
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
        node.text = 'pv2web_ro/PvWatch'
        node = etree.SubElement(root, "datetime")
        node.text = str(utils.getTime()).split('.')[0]
    
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
        utils.writeFile(abs_raw_xml, xmlText)
        utils.copyToWebServer(abs_raw_xml, raw_xml)
    
        #--- xslt transforms from XML to HTML
    
        # make the index.html file
        index_html = self.configuration['HTML_INDEX_FILE']  # short name
        abs_index_html = os.path.join(localDir, index_html)  # absolute path
        utils.xslt_transformation(self.configuration['LIVEDATA_XSL_STYLESHEET'], abs_raw_xml, abs_index_html)
        utils.copyToWebServer(abs_index_html, index_html)  # copy to XSD
    
        # display the raw data (but pre-convert it in an html page)
        raw_html = self.configuration['HTML_RAWREPORT_FILE']
        abs_raw_html = os.path.join(localDir, raw_html)
        utils.xslt_transformation(self.configuration['RAWTABLE_XSL_STYLESHEET'], abs_raw_xml, abs_raw_html)
        utils.copyToWebServer(abs_raw_html, raw_html)
    
        # also copy the raw table XSLT
        xslFile = self.configuration['RAWTABLE_XSL_STYLESHEET']
        utils.copyToWebServer(os.path.join(localDir, xslFile), xslFile)
