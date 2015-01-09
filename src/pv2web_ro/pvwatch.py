#!/usr/bin/env python

'''
watch EPICS process variables and periodically write them to a file and post to static web site

Start this with the shell command::

    python ./pvwatch.py >>& log.txt

'''


import datetime         # date/time stamps
import os.path          # testing if a file exists
import shlex            # parsing command lines (for xsltproc)
import shutil           # file copies
import subprocess       # calling other software (xsltproc)
import sys              # for flushing log output
import time             # provides sleep()
# TODO: refactor to use lxml
from xml.dom import minidom
from xml.etree import ElementTree
import epics            # manages EPICS (PyEpics) connections for Python 2.6+
# TODO: generalize wwwServerTransfers to support localConfig
import wwwServerTransfers
import traceback
import numpy


global GLOBAL_MONITOR_COUNTER
global pvdb         # cache of last known good values
global xref         # cross-reference between mnemonics and PV names: {mne:pvname}

GLOBAL_MONITOR_COUNTER = 0
pvdb = {}   # EPICS data will go here
xref = {}   # cross-reference id with PV
PVLIST_FILE = "pvlist.xml"
MAINLOOP_COUNTER_TRIGGER = 10000  # print a log message periodically
USAXS_DATA = None

PVWATCH_INDEX_PV = '15iddLAX:long20'
PVWATCH_PID_PV   = '15iddLAX:long19'
PVWATCH_REF_PV   = '15iddLAX:long18'


'''value for expected EPICS PV is None'''
class NoneEpicsValue(Exception): pass

'''pv not in pvdb'''
class PvNotRegistered(Exception): pass


def logMessage(msg):
    '''write a message with a timestamp and pid to the log file'''
    # TODO: refactor to use logging package
    scriptName = os.path.basename(sys.argv[0])
    print "[%s %d %s] %s" % (scriptName, os.getpid(), getTime(), msg)
    sys.stdout.flush()


def logException(troublemaker):
    '''write an exception report to the log file'''
    msg = "problem with %s:" % troublemaker
    for _ in msg.splitlines():
        logMessage(_)
    for _ in traceback.format_exc().splitlines():
        logMessage('\t' + _)


def update_pvdb(pv, raw_value):
    if pv not in pvdb:
        msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
        raise PvNotRegistered, msg
    entry = pvdb[pv]
    # ch = entry['ch']
    entry['timestamp'] = getTime()
    entry['counter'] += 1
    entry['raw_value'] = raw_value
    entry['value'] = entry['format'] % raw_value


def EPICS_monitor_receiver(*args, **kws):
    '''Response to an EPICS (PyEpics) monitor on the channel'''
    global GLOBAL_MONITOR_COUNTER
    pv = kws['pvname']
    if pv not in pvdb:
        msg = '!!!ERROR!!! %s was not found in pvdb!' % pv
        raise PvNotRegistered, msg
    update_pvdb(pv, kws['value'])   # cache the last known good value
    GLOBAL_MONITOR_COUNTER += 1


def add_pv(mne, pv, desc, fmt):
    '''Connect to another EPICS (PyEpics) process variable'''
    if pv in pvdb:
        raise Exception("key '%s' already defined by id=%s" % (pv, pvdb[pv]['id']))
    ch = epics.PV(pv)
    #ch.connect()
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
    pvdb[pv] = entry
    xref[mne] = pv            # mne is local mnemonic, define actual PV in pvlist.xml
    ch.add_callback(EPICS_monitor_receiver)  # start callbacks now
    cv = ch.get_ctrlvars()
    unit_renames = {		# handle some non SI unit names
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
    update_pvdb(pv, ch.get())   # initialize the cache


def getSpecFileName(pv):
    '''construct the name of the file, based on a PV'''
    dir_pv = xref['spec_dir']
    userDir = pvdb[dir_pv]['value']
    rawName = pvdb[pv]['value']
    if userDir is None:
        raise NoneEpicsValue, '"None" received for spec_dir PV: <' + str(dir_pv) + '>'
    if rawName is None:
        raise NoneEpicsValue, '"None" received for spec file PV: <' + str(pv) + '>'
    specFile = userDir + "/" + rawName
    return specFile


def writeFile(output_file, contents):
    '''write contents to file'''
    f = open(output_file, 'w')
    f.write(contents)
    f.close()


def xslt_transformation(xslt_file, src_xml_file, result_xml_file):
    '''transform an XML file using an XSLT'''
    # see: http://lxml.de/xpathxslt.html#xslt
    from lxml import etree as lxml_etree      # in THIS routine, use lxml's etree
    src_doc = lxml_etree.parse(src_xml_file)
    xslt_doc = lxml_etree.parse(xslt_file)
    transform = lxml_etree.XSLT(xslt_doc)
    result_doc = transform(src_doc)
    buf = lxml_etree.tostring(result_doc, pretty_print=True)
    writeFile(result_xml_file, buf)


def shellCommandToFile(command, outFile):
    '''execute a shell command and write its output to a file'''
    p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
    f = p.stdout
    p.wait()
    buf = f.read()
    f.close()
    writeFile(outFile, buf)


def debugging_diagnostic(code):
    epics.caput(PVWATCH_REF_PV, code)


def buildReport():
    '''build the report'''
    root = ElementTree.Element("pv2web_ro")
    root.set("version", "1")
    node = ElementTree.SubElement(root, "written_by")
    node.text = 'pv2web_ro/pvwatch'
    node = ElementTree.SubElement(root, "datetime")
    node.text = str(datetime.datetime.now()).split('.')[0]

    sorted_id_list = sorted(xref)
    fields = ("name", "id", "description", "timestamp",
              "counter", "units", "value", "raw_value", "format")

    for mne in sorted_id_list:
        pv = xref[mne]
        entry = pvdb[pv]

        node = ElementTree.SubElement(root, "pv")
        node.set("id", mne)
        node.set("name", pv)

        for item in fields:
            subnode = ElementTree.SubElement(node, item)
            subnode.text = str(entry[item])

    global USAXS_DATA
    if USAXS_DATA is not None and USAXS_DATA.get('usaxs', None) is not None:
        try:
            specfile = USAXS_DATA['file']
            node = ElementTree.SubElement(root, "usaxs_scans")
            node.set("file", specfile)
            for scan in USAXS_DATA['usaxs']:
                scannode = ElementTree.SubElement(node, "scan")
            for item in ('scan', 'key', 'label'):
                scannode.set(item, str(scan[item]))
            scannode.set('specfile', specfile)
            ElementTree.SubElement(scannode, "title").text = scan['title']
            # write the scan data to the XML file
            vec = ElementTree.SubElement(scannode, "Q")
            vec.set('units', '1/A')
            vec.text = ' '.join(textArray(scan['qVec']))
            vec = ElementTree.SubElement(scannode, "R")
            vec.set('units', 'arbitrary')
            vec.text = ' '.join(textArray(scan['rVec']))
        except Exception, e:
            logMessage('caught Exception while writing USAXS scan data to XML file')
            logMessage('  file: %s' % specfile)
            logMessage(e)

    # final steps
    # ProcessingInstruction for 2nd line of XML
    # Cannot place this with ElementTree where it is needed
    # use minidom
    doc = minidom.parseString(ElementTree.tostring(root))
    # <?xml-stylesheet type="text/xsl" href="raw-table.xsl" ?>
    # insert XML Processing Instruction text after first line of XML
    pi = doc.createProcessingInstruction('xml-stylesheet',
                                     'type="text/xsl" href="raw-table.xsl"')
    root = doc.firstChild
    doc.insertBefore(pi, root)
    xmlText = doc.toxml()       # all on one line, looks bad, who cares?
    #xmlText = doc.toprettyxml(indent = "  ") # toprettyxml() adds extra unwanted whitespace
    return xmlText


def textArray(arr):
    '''convert an ndarray to a text array'''
    if isinstance(arr, numpy.ndarray):
        return [str(_) for _ in arr]
    return arr


def report():
    '''write the values out to files'''
    debugging_diagnostic(2)

    xmlText = buildReport()
    debugging_diagnostic(20)

    # WWW directory for livedata (absolute path)
    localDir = localConfig.LOCAL_WWW_LIVEDATA_DIR

    #--- write the XML with the raw data from EPICS
    raw_xml = localConfig.XML_REPORT_FILE
    abs_raw_xml = os.path.join(localDir, raw_xml)
    writeFile(abs_raw_xml, xmlText)
    debugging_diagnostic(21)
    wwwServerTransfers.scpToWebServer(abs_raw_xml, raw_xml)
    debugging_diagnostic(22)

    #--- xslt transforms from XML to HTML

    # make the index.html file
    index_html = localConfig.HTML_INDEX_FILE  # short name
    abs_index_html = os.path.join(localDir, index_html)  # absolute path
    xslt_transformation(localConfig.LIVEDATA_XSL_STYLESHEET, abs_raw_xml, abs_index_html)
    debugging_diagnostic(23)
    wwwServerTransfers.scpToWebServer(abs_index_html, index_html)  # copy to XSD
    debugging_diagnostic(24)

    # display the raw data (but pre-convert it in an html page)
    raw_html = localConfig.HTML_RAWREPORT_FILE
    abs_raw_html = os.path.join(localDir, raw_html)
    xslt_transformation(localConfig.RAWTABLE_XSL_STYLESHEET, abs_raw_xml, abs_raw_html)
    debugging_diagnostic(25)
    wwwServerTransfers.scpToWebServer(abs_raw_html, raw_html)
    debugging_diagnostic(26)

    # also copy the raw table XSLT
    xslFile = localConfig.RAWTABLE_XSL_STYLESHEET
    wwwServerTransfers.scpToWebServer(os.path.join(localDir, xslFile), xslFile)

    # make the usaxstv.html file
    usaxstv_html = localConfig.HTML_USAXSTV_FILE  # short name
    abs_usaxstv_html = os.path.join(localDir, usaxstv_html)  # absolute path
    xslt_transformation(localConfig.USAXSTV_XSL_STYLESHEET, abs_raw_xml, abs_usaxstv_html)
    debugging_diagnostic(27)
    wwwServerTransfers.scpToWebServer(abs_usaxstv_html, usaxstv_html)  # copy to XSD
    debugging_diagnostic(28)


def getTime():
    '''return a datetime value'''
    dt = datetime.datetime.now()
    return dt


def _initiate_PV_connections():
    '''create connections to all defined PVs'''
    if not os.path.exists(PVLIST_FILE):
        logMessage('could not find file: ' + PVLIST_FILE)
        return
    try:
        tree = ElementTree.parse(PVLIST_FILE)
    except:
        logMessage('could not parse file: ' + PVLIST_FILE)
        return

    for key in tree.findall(".//EPICS_PV"):
        if key.get("_ignore_", "false").lower() == "false":
            mne = key.get("mne")
            pv = key.get("PV")
            desc = key.get("description")
            fmt = key.get("display_format", "%s")  # default format
            try:
                add_pv(mne, pv, desc, fmt)
            except:
                msg = "%s: problem connecting: %s" % (PVLIST_FILE, ElementTree.tostring(key))
                logException(msg)


def _periodic_reporting_task(mainLoopCount, nextReport, nextLog, delta_report, delta_log):
    global GLOBAL_MONITOR_COUNTER
    global MAINLOOP_COUNTER_TRIGGER
    dt = getTime()
    epics.ca.poll()

    if mainLoopCount == 0:
        logMessage(" %s times through main loop" % MAINLOOP_COUNTER_TRIGGER)

    if dt >= nextReport:
        nextReport = dt + delta_report

        try: report()                                   # write contents of pvdb to a file
        except Exception: logException("report()")

    if dt >= nextLog:
        debugging_diagnostic(1)
        nextLog = dt + delta_log
        msg = "checkpoint, %d EPICS monitor events received" % GLOBAL_MONITOR_COUNTER
        logMessage(msg)
        GLOBAL_MONITOR_COUNTER = 0  # reset

    return nextReport, nextLog


def main():
    '''
    run the main loop
    '''
    global GLOBAL_MONITOR_COUNTER
    test_pv = 'S:SRcurrentAI'
    epics.caget(test_pv)
    ch = epics.PV(test_pv)
    epics.ca.poll()
    connected = ch.connect(timeout=5.0)
    if not connected:
        print 'Did not connect PV:', ch, '  program has exited'
        return

    logMessage("starting pvwatch.py")
    _initiate_PV_connections()

    logMessage("Connected %d EPICS PVs" % len(pvdb))
    epics.caput(PVWATCH_INDEX_PV+'.DESC', 'pvwatch mainLoopCounter')
    epics.caput(PVWATCH_PID_PV+'.DESC', 'pvwatch PID')
    epics.caput(PVWATCH_REF_PV+'.DESC', 'pvwatch reference')
    epics.caput(PVWATCH_INDEX_PV, -1)
    epics.caput(PVWATCH_PID_PV, os.getpid())
    debugging_diagnostic(-1)

    nextReport = getTime()
    nextLog = nextReport
    delta_report = datetime.timedelta(seconds=localConfig.REPORT_INTERVAL_S)
    delta_log = datetime.timedelta(seconds=localConfig.LOG_INTERVAL_S)
    mainLoopCount = 0
    while True:
        debugging_diagnostic(0)
        mainLoopCount = (mainLoopCount + 1) % MAINLOOP_COUNTER_TRIGGER
        nextReport, nextLog = _periodic_reporting_task(mainLoopCount,
                                       nextReport, nextLog, delta_report, delta_log)
        epics.caput(PVWATCH_INDEX_PV, mainLoopCount)
        time.sleep(localConfig.SLEEP_INTERVAL_S)

    # this exit handling will never be called
    for pv in pvdb:
        ch = pvdb[pv]['ch']
        if ch != None:
            ch.disconnect()
    print "script is done"


if __name__ == '__main__':
    main()
