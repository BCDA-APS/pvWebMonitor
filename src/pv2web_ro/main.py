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

        self.nextReport = getTime()
        self.nextLog = self.nextReport
        self.delta_report = datetime.timedelta(seconds=configuration['REPORT_INTERVAL_S'])
        self.delta_log = datetime.timedelta(seconds=configuration['LOG_INTERVAL_S'])
        self.mainLoopCount = 0
    
    def start(self):
        '''begin receiving PV updates and posting new web content'''
        pass
    
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
