..
  This file describes user-visible changes between the versions.

  subsections could include these headings (in this order), omit if no content

    Notice
    Breaking Changes
    New Features and/or Enhancements
    Fixes
    Maintenance
    Deprecations
    Contributors

Change History
##############

The project `milestones <https://github.com/BCDA-APS/pvWebMonitor/milestones>`_
describe the future plans.

..
   2021.0.1
   ************

   release expected by TBA

2021.0.0
************

release expected by 2022-11-18

Breaking Changes
------------------------

* Dropped support for Python <3.8 (includes Python 2)

------------

:2021.0.0: release expected by 2020-12-18

    * first python 2.8 release

:2020.0.0: released 2020-09-24

    * last python 2.7 release

:2017.1211.1:        use Python versioneer
:2017.1211.0:        ``as_string`` attribute
:2016.1025.0:        revise the versioning process
:2016.1003.2:        `issue #22 <https://github.com/prjemian/pvWebMonitor/issues/22>`_: correct version number shown now
:2016.0907.0:        `issue #18 <https://github.com/prjemian/pvWebMonitor/issues/18>`_: check XSLT files for syntax errors,
                     `issue #19 <https://github.com/prjemian/pvWebMonitor/issues/19>`_: let user choose to write waveform strings as string or array of integers,
                     `issue #20 <https://github.com/prjemian/pvWebMonitor/issues/20>`_: add username and host to logging messages
:2016.0516.2:        #16: accept both version 1.0 & 1.0.1 config.xml files
:2016.0427.1:        #12: user can add additional file extension patterns, improve the setup of manage.sh on Linux
:2016.0414.2:        #9: resolve ValueError when creating XML declaration
:2015.0117.0:        #6: rename project to pvWebMonitor
:2015.0116.0:        #13: management shell script now uses /bin/bash
:2015.0115.0:        #4: refactor XSLT infrastructure and web site
:2015.0114.1:        include XML infrastructure in package
:2015.0114.0:        packaging update
:2015.0113.1:        add --setup to fill a new project directory with needed files
:2015.0113.0:        validate all XML files and raise exceptions if invalid
:2015.0112.2:        documentation at ReadTheDocs, package at PyPI, code at GitHub
:2015-01-09 v1.0.0:  initial conversion from USAXS livedata project
