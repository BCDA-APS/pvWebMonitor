.. _pvWebMonitor:

============
pvWebMonitor
============

**NOTE**:  We are moving this repository in 2020-Q3!  See https://github.com/prjemian/pvWebMonitor/issues/39

**post EPICS PVs to read-only (static) web page(s)**

This package provides a background service that monitors EPICS PVs 
and writes them into customized HTML files in a WWW server 
directory.  The service can be started and stopped by a manage.csh 
script for automated startup in a cron task or at system startup.

:author: 	Pete R. Jemian
:email:  	jemian@anl.gov
:copyright: 2005-2017, UChicago Argonne, LLC
:license:   ANL OPEN SOURCE LICENSE (see *LICENSE*)
:docs:      http://pvWebMonitor.readthedocs.io
:git:       https://github.com/prjemian/pvWebMonitor.git
:PyPI:      https://pypi.python.org/pypi/pvWebMonitor

:publishing:
   .. image:: https://img.shields.io/github/tag/prjemian/pvWebMonitor.svg
      :target: https://github.com/prjemian/pvWebMonitor/tags
   .. image:: https://img.shields.io/github/release/prjemian/pvWebMonitor.svg
      :target: https://github.com/prjemian/pvWebMonitor/releases
   .. .. image:: https://img.shields.io/pypi/pyversions/pvWebMonitor.svg
      :target: https://pypi.python.org/pypi/pvWebMonitor
   .. image:: https://img.shields.io/pypi/v/pvWebMonitor.svg
      :target: https://pypi.python.org/pypi/pvWebMonitor/

:review:
   .. image:: https://app.codacy.com/project/badge/Grade/ee4a888d573247afb54c1f6f53d503bd    
      :target: https://www.codacy.com/manual/prjemian/pvWebMonitor/dashboard?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=prjemian/pvWebMonitor&amp;utm_campaign=Badge_Grade
