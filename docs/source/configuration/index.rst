Configuration
=============

These are the steps needed to get the **pvWebMonitor** 
service running on your workstation.

#. install the *pvWebMonitor* package into your Python environment
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
   rawdata
   livedata
   manage
