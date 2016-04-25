'''
pvWebMonitor.pvwatch
'''

# Copyright (c) 2005-2016, UChicago Argonne, LLC.
# See LICENSE file for details.


import datetime
import epics
import fnmatch
from lxml import etree
import numpy
import os
import time
import utils


XML_SCHEMA_FILE = 'pvlist.xsd'
XML_RAWDATA_FILE_NAME = 'rawdata.xml'
XSL_PVLIST_FILE_NAME = 'pvlist.xsl'
XSL_RAWDATA_FILE_NAME = 'rawdata.xsl'
XSL_INDEX_FILE_NAME = 'index.xsl'


class PvNotRegistered(Exception): 
    '''pv not in pvdb'''
    pass

class CouldNotParseXml(Exception): 
    '''Could not parse XML file'''
    pass


def _xslt_(xslt_file, source_xml_file):
    '''
    convenience routine for XSLT transformations
    
    For a given XSLT file *abcdefg.xsl*, will produce a file *abcdefg.html*::

        abcdefg.xsl + xml_data  --> abcdefg.html
    
    '''
    output_xml_file = os.path.splitext(xslt_file)[0] + os.extsep + 'html'
    utils.xslt_transformation(xslt_file, source_xml_file, output_xml_file)


class PvWatch(object):
    '''
    Core function of the pvWebMonitor package
    
    To call this code, first define ``configuration=dict()`` with terms
    as defined in :meth:`read_config.read_xml`, then statements such as:

    .. code-block:: python
       :linenos:
    
        watcher = PvWatch(configuration)
        watcher.start()
    
    '''
    
    def __init__(self, configuration):
        self.configuration = configuration  # from XML configuration file
        self.pvdb = {}      # cache of last known good values
        self.xref = {}      # cross-reference between mnemonics and PV names: {mne:pvname}
        self.monitor_counter = 0
        self.upload_patterns = configuration['PATTERNS']

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
        
        utils.validate(tree, XML_SCHEMA_FILE)

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

        # report the RTYP (record type, if available)
        basename = pv.split('.')[0]
        field = pv[len(basename):]
        rtyp_pv = epics.PV(basename + '.RTYP')
        rtyp = rtyp_pv.get() or 'unknown'
        if basename == pv or field == '.VAL':
            entry['record_type'] = rtyp
        else:
            # field of record
            entry['record_type'] = rtyp + field

        # FIXME: what to do if PV did not connect? (ch.connected == False)

        self.update_pvdb(pv, ch.get())   # initialize the cache

    def add_file_pattern(self, pattern):
        '''
        add ``pattern`` as an additional file extension pattern
        
        Any file with extension matching any of the patterns in 
        ``self.upload_patterns`` will copied to the
        WWW directory, if they are newer.
        '''
        self.upload_patterns.append(pattern)

    def update_pvdb(self, pv, raw_value):
        '''
        log PV value to the cache in pvdb

        :param str pv: name of EPICS PV
        :param obj raw_value: could be str, float, int, or ...
        '''
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
        root = etree.Element("pvWebMonitor")
        root.set("version", "1")
        node = etree.SubElement(root, "written_by")
        node.text = 'pvWebMonitor/PvWatch'
        node = etree.SubElement(root, "datetime")
        node.text = str(utils.getTime()).split('.')[0]
    
        sorted_id_list = sorted(self.xref)
        fields = ("name", "id", "description", "timestamp", "record_type",
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

        try:
            pi_xml = etree.ProcessingInstruction('xml', 'version="1.0"')
            xmlText = etree.tostring(pi_xml, pretty_print=True)
        except ValueError:
            # some instanced of lxml raise a ValueError saying that 'xml' is not allowed
            xmlText = '<?xml version="1.0" ?>\n'
        pi_xsl = etree.ProcessingInstruction('xml-stylesheet', 'type="text/xsl" href="pvlist.xsl"')
        xmlText += etree.tostring(pi_xsl, pretty_print=True)
        xmlText += etree.tostring(root, pretty_print=True)

        return xmlText

    def report(self):
        '''
        write the values out to files
        
        The values of the monitored EPICS PVs (the "raw data")
        is written to an XML file.  This file is then used
        with one or more XSLT stylesheets to create HTML pages.
        An overall "home page" (index.html) is created to provide
        a table of contents of this static web site.
        '''
        xmlText = self.buildReport()
        utils.writeFile(XML_RAWDATA_FILE_NAME, xmlText)
        
        # accumulate list of each file written below
        www_site_file_list = []
        xslt_file_list_used = ['index.xsl', ]  # do the index.xsl file last
        www_site_file_list.append(XML_RAWDATA_FILE_NAME)
    
        # add pvlist.xml to file list
        pvlist_xml_file_name = self.configuration['PVLIST_FILE']
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
        for file_pattern in self.upload_patterns:
            www_site_file_list += fnmatch.filter(local_files, file_pattern)
            www_site_file_list += fnmatch.filter(local_files, file_pattern.upper())
        
        # only copy files if web_site_path is not the current dir
        www_site_file_list = sorted(set(www_site_file_list))
        www_site_path = os.path.abspath(self.configuration['LOCAL_WWW_LIVEDATA_DIR'])
        if www_site_path != os.path.abspath(os.getcwd()):
            for fname in www_site_file_list:
                utils.copyToWebServer(fname, www_site_path)
