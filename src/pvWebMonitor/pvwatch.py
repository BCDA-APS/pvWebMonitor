"""
pvWebMonitor.pvwatch
"""

# Copyright (c) 2005-2022, UChicago Argonne, LLC.
# See LICENSE file for details.


from . import utils
from lxml import etree
from ophyd.signal import EpicsSignalBase
import datetime
import epics
import fnmatch
import logging
import ophyd
import os
import time


logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")
XML_SCHEMA_FILE = "pvlist.xsd"
XML_RAWDATA_FILE_NAME = "rawdata.xml"
XSL_PVLIST_FILE_NAME = "pvlist.xsl"
XSL_RAWDATA_FILE_NAME = "rawdata.xsl"
XSL_INDEX_FILE_NAME = "index.xsl"

ophyd.set_cl("PyEpics".lower())
# set default timeout for all EpicsSignal connections & communications
TIMEOUT = 60
if not EpicsSignalBase._EpicsSignalBase__any_instantiated:
    EpicsSignalBase.set_defaults(
        auto_monitor=True,
        timeout=TIMEOUT,
        write_timeout=TIMEOUT,
        connection_timeout=TIMEOUT,
    )


class PvNotRegistered(Exception):
    """PV not in 'pvdb'."""


class CouldNotParseXml(Exception):
    """Could not parse XML file."""


def _xslt_(xslt_file, source_xml_file):
    """
    Convenience routine for XSLT transformations.

    For a given XSLT file *abcdefg.xsl*, will produce a file *abcdefg.html*::

        abcdefg.xsl + xml_data  --> abcdefg.html

    """
    output_xml_file = os.path.splitext(xslt_file)[0] + os.extsep + "html"
    utils.xslt_transformation(xslt_file, source_xml_file, output_xml_file)


class PvCrossReference:
    """
    Maintain cross-references between pvnames, mnemonics, and their signals.
    """

    def __init__(self) -> None:
        self.clear()

    def __len__(self):
        return len(self.pv_ref)

    def clear(self):
        """Delete the cross-references tables."""
        self.pv_ref = {}  # pvname: signal
        self.mne_ref = {}  # mnemonic: pvname

    def add(self, pv, mne, entry):
        """Collect a new PV name, mnemonic, and PvEntry entry object."""
        if pv in self.pv_ref:
            raise KeyError(f"'{pv}' is already known.")
        self.pv_ref[pv] = entry
        self.mne_ref[mne] = pv

    def get(self, key):
        """Lookup an entry by PV or mnemonic."""
        if key in self.pv_ref:
            return self.pv_ref[key]
        if key in self.mne_ref:
            return self.get(self.mne_ref[key])
        raise KeyError(f"'{key}' not found.")

    def known(self, pv):
        """Is this PV known?"""
        return pv in self.pv_ref

    @property
    def mnemonics(self):
        """List the known mnemonics."""
        return self.mne_ref.keys()

    @property
    def pvnames(self):
        """List the known PV names."""
        return self.pv_ref.keys()


class PvEntry:
    """
    Monitor (read-only) a single EPICS PV.
    """

    def __init__(
        self,
        mnemonic,
        pvname,
        as_string=False,
        description=None,
        fmt="%s",
    ):
        self.as_string: bool = as_string  # return string representation of the value
        self.description: str = description  # text description for humans
        self.fmt: str = fmt  # format for display
        self.mnemonic: str = mnemonic  # symbolic name used in the python code
        self.pvname: str = pvname  # EPICS PV name

        self.char_value: str = None  # string value
        self.counter: int = 0  # number of monitor events received
        self.raw_value: str = None  # unformatted value
        self.record_type: str = None  # EPICS record type
        self.signal_ro = ophyd.EpicsSignalRO(pvname, name=mnemonic)  # EPICS PV
        self.timestamp: object = None  # client time last monitor was received
        self.units: str = None  # engineering units
        self.value: str = None  # formatted value

        self.signal_ro.subscribe(self.ca_monitor_event)
        self.learn_units()

    def __repr__(self):
        return (
            f"{self.__class__.__name__}("
            f"pvname='{self.pvname}'"
            f", mnemonic='{self.mnemonic}'"
            f", description='{self.description}'"
            f", as_string='{self.as_string}'"
            f", connected='{self.connected}'"
            ")"
        )

    def __str__(self):
        return (
            f"{self.__class__.__name__}("
            f"pvname='{self.pvname}'"
            f", mnemonic='{self.mnemonic}'"
            f", description='{self.description}'"
            f", as_string='{self.as_string}'"
            ")"
        )

    @property
    def connected(self):
        """Is EPICS connected?"""
        return self.signal_ro is not None and self.signal_ro.connected

    def ca_monitor_event(self, **kwargs):
        """Respond to an EPICS CA monitor event."""
        if "value" in kwargs:
            self.counter += 1
            self.raw_value = kwargs["value"]
            timestamp = kwargs["timestamp"]

            self.value = self.fmt % self.raw_value
            self.char_value = str(self.value)
            dt = datetime.datetime.fromtimestamp(timestamp)
            self.timestamp = dt.isoformat(timespec="seconds")  # as ISO8601
            # logger.info("%r: kwargs: %s", self, kwargs)

    def learn_units(self):
        """
        Learn the units from EPICS, adjust for 'user names', as known.
        """
        md = self.signal_ro.metadata

        unit_renames = {  # handle some non SI unit names
            # old      new
            "millime": "mm",
            "millira": "mr",
            "degrees": "deg",
            "Volts": "V",
            "VDC": "V",
            "eng": "",
        }
        units = md.get("units")
        if units is not None:
            if units in unit_renames:
                units = unit_renames[units]
            self.units = units

    def learn_record_type(self):
        """
        Record the EPICS RTYP (record type, if available).
        """
        basename = self.pvname.split(".")[0]
        field = self.pvname[len(basename) :]
        rtyp_pv = epics.PV(basename + ".RTYP")  # use PyEpics here
        rtyp = rtyp_pv.get() or "unknown"
        if basename == self.pvname or field == ".VAL":
            self.record_type = rtyp
        else:
            # field of record
            self.record_type = rtyp + field


class PvWatch(object):
    """
    Core of the pvWebMonitor package.

    To call this code, first define ``configuration=dict()`` with terms
    as defined in :meth:`read_config.read_xml`, then statements such as:

    .. code-block:: python
       :linenos:

        watcher = PvWatch(configuration)
        watcher.start()

    """

    def __init__(self, configuration):
        self.configuration = configuration  # from XML configuration file
        self.pvdb = PvCrossReference()  # cache of last known good values
        self.monitor_counter = 0
        self.upload_patterns = configuration["PATTERNS"]

        self.get_pvlist()
        logger.debug("read list of PVs to monitor")

    def start(self):
        """begin receiving PV updates and posting new web content"""
        log_deadline = time.time()
        log_interval = self.configuration["LOG_INTERVAL_S"]
        report_deadline = time.time()
        report_interval = self.configuration["REPORT_INTERVAL_S"]
        mainLoopCount = 0
        mainLoopCountRollover = self.configuration["MAINLOOP_COUNTER_TRIGGER"]
        sleepInterval = self.configuration["SLEEP_INTERVAL_S"]

        while True:
            mainLoopCount = (mainLoopCount + 1) % mainLoopCountRollover
            if mainLoopCount == 0:
                logger.debug(" %s times through main loop", mainLoopCountRollover)

            t_now = time.time()

            if t_now >= report_deadline:
                report_deadline = time.time() + report_interval
                print(f"New report deadline: {report_deadline}")
                logger.debug("reporting ...")

                try:
                    self.report()  # write contents of pvdb to a file
                except Exception as exc:
                    logger.debug("exception: %s", exc)

            if t_now >= log_deadline:
                log_deadline = time.time() + log_interval
                logger.debug(
                    "checkpoint, %d EPICS monitor events received", self.monitor_counter
                )
                self.monitor_counter = 0  # reset

            time.sleep(sleepInterval)

    def get_pvlist(self):
        """get the PVs from the XML file"""
        pvlist_file = self.configuration["PVLIST_FILE"]
        if not os.path.exists(pvlist_file):
            logger.debug("could not find file: %s", pvlist_file)
            return
        try:
            tree = etree.parse(pvlist_file)
        except Exception as exc:
            raise CouldNotParseXml(f"could not parse file '{pvlist_file}': {exc}")

        utils.validate(tree, XML_SCHEMA_FILE)
        logger.debug("validated file: '%s'", pvlist_file)

        for key in tree.findall(".//EPICS_PV"):
            if key.get("_ignore_", "false").lower() == "false":
                mne = key.get("mne")
                pv = key.get("PV")
                desc = key.get("description")
                fmt = key.get("display_format", "%s")  # default format
                as_string = key.get("as_string", False)  # default format
                # :see: http://cars9.uchicago.edu/software/python/pyepics3/pv.html?highlight=as_string#pv.get
                try:
                    self.add_pv(mne, pv, desc, fmt, as_string)
                except Exception as exc:
                    logger.warning(
                        "'%s': problem connecting '%s': %s",
                        pvlist_file,
                        utils.etree_as_str(key),
                        exc,
                    )

        logger.debug("all PVs added")

    def add_pv(self, mne, pv, desc, fmt, as_string):
        """Connect to a EPICS (PyEpics) process variable"""
        if self.pvdb.known(pv):
            raise KeyError(f"PV '{pv}' already defined.")

        entry = PvEntry(mne, pv, description=desc, fmt=fmt, as_string=as_string)
        self.pvdb.add(pv, mne, entry)

        if not entry.connected:
            logger.debug("PV not connected yet: %s", pv)

    def add_file_pattern(self, pattern):
        """
        add ``pattern`` as an additional file extension pattern

        Any file with extension matching any of the patterns in
        ``self.upload_patterns`` will copied to the
        WWW directory, if they are newer.
        """
        self.upload_patterns.append(pattern)

    def buildReport(self):
        """build the report"""
        root = etree.Element("pvWebMonitor")
        root.set("version", "1")
        node = etree.SubElement(root, "written_by")
        node.text = "pvWebMonitor/PvWatch"
        node = etree.SubElement(root, "datetime")
        node.text = datetime.datetime.now().isoformat(timespec="seconds")

        fields = (
            "pvname",
            "mnemonic",
            "description",
            "timestamp",
            "record_type",
            "counter",
            "units",
            "value",
            "char_value",
            "raw_value",
            "fmt",
        )

        for mne in sorted(self.pvdb.mnemonics):
            entry = self.pvdb.get(mne)
            pv = entry.pvname

            node = etree.SubElement(root, "pv")
            node.set("id", mne)
            node.set("name", pv)

            for item in fields:
                subnode = etree.SubElement(node, item)
                subnode.text = str(getattr(entry, item))

        xmlText = '<?xml version="1.0" ?>'
        pi_xsl = etree.ProcessingInstruction(
            "xml-stylesheet", 'type="text/xsl" href="pvlist.xsl"'
        )
        xmlText += f"\n{utils.etree_as_str(pi_xsl)}" f"\n{utils.etree_as_str(root)}"

        return xmlText

    def report(self):
        """
        write the values out to files

        The values of the monitored EPICS PVs (the "raw data")
        is written to an XML file.  This file is then used
        with one or more XSLT stylesheets to create HTML pages.
        An overall "home page" (index.html) is created to provide
        a table of contents of this static web site.
        """
        xmlText = self.buildReport()
        utils.writeFile(XML_RAWDATA_FILE_NAME, xmlText)

        # accumulate list of each file written below
        www_site_file_list = []
        xslt_file_list_used = [
            "index.xsl",
        ]  # do the index.xsl file last
        www_site_file_list.append(XML_RAWDATA_FILE_NAME)

        # add pvlist.xml to file list
        pvlist_xml_file_name = self.configuration["PVLIST_FILE"]
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
                xslt_files = fnmatch.filter(os.listdir("."), "*.xsl")
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
        local_files = os.listdir(".")
        for file_pattern in self.upload_patterns:
            www_site_file_list += fnmatch.filter(local_files, file_pattern)
            www_site_file_list += fnmatch.filter(local_files, file_pattern.upper())

        # only copy files if web_site_path is not the current dir
        www_site_file_list = sorted(set(www_site_file_list))
        www_site_path = os.path.abspath(self.configuration["LOCAL_WWW_LIVEDATA_DIR"])
        if www_site_path != os.path.abspath(os.getcwd()):
            for fname in www_site_file_list:
                utils.copyToWebServer(fname, www_site_path)

    def pv_connected(self, pvname):
        """Is the named PV connected?"""
        if self.pvdb.known(pvname):
            return self.pvdb.get(pvname).connected
        return False

    def get(self, pvname):
        """Return the PvEntry object for the named PV."""
        return self.pvdb.get(pvname)
