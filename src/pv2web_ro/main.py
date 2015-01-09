#!/usr/bin/env python

'''
pv2web_ro
'''

# Copyright (c) 2005-2015, UChicago Argonne, LLC.
# See LICENSE file for details.


import datetime
import epics
import logging
import lxml
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
            tree = lxml.etree.parse(pvlist_file)
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
                    msg = "%s: problem connecting: %s" % (pvlist_file, lxml.etree.tostring(key))
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

    parser.add_argument('-v', '--version', action='version', version=pv2web_ro.__version__)

    user_args = parser.parse_args()

    configuration = read_config.read_xml(user_args.xml_config_file)
    watcher = pvwatch(configuration)
    watcher.start()


if __name__ == '__main__':
    '''simple test program for developers'''
    sys.argv.append('config.xml')
    #sys.argv.append('-h')
    #sys.argv.append('-v')
    main()
