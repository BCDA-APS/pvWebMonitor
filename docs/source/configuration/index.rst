Configuration
=============

.. note:: -tba-

.. issue #3
   needs additional feature for users to setup a new project config directory
   Add this to the command line options with "--initialize" requiring a destination directory.
   Raise exceptions if the destination directory has files that would be overwritten.

These are the steps needed to get the **pv2web_ro** 
service running on your workstation.

#. install the *pv2web_ro* package into your Python environment
#. setup the project configuration directory
#. identify the web server directory to be used
#. edit config.xml
#. identify the list of EPICS PVs
#. edit pvlist.xml
#. customize the livedata display file: edit livedata.xsl
#. run the config.xml file
#. watch the log_data.txt file in the project directory

These steps are described in the following sections:

.. toctree::
   :maxdepth: 2
   :glob:

   install
   setup
   config
   pvlist
   livedata
   raw_table
   manage
