.. _pv2web_ro:

=========
pv2web_ro
=========

**post EPICS PVs to read-only (static) web page(s)**

:author: 	Pete R. Jemian
:email:  	jemian@anl.gov
:copyright: 2005-2015, UChicago Argonne, LLC
:license:   ANL OPEN SOURCE LICENSE (see *LICENSE*)
:docs:      http://pv2web_ro.readthedocs.org
:git:       https://github.com/prjemian/pv2web_ro.git
:PyPI:      https://pypi.python.org/pypi/pv2web_ro 


This package provides a background service that monitors EPICS PVs 
and writes them into customized HTML files in a WWW server 
directory.  The service can be started and stopped by a manage.csh 
script for automated startup in a cron task or at system startup.
