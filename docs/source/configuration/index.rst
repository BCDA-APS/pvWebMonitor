Configuration
=============

.. note:: -tba-

.. issue #3
   needs additional feature for users to setup a new project config directory
   Add this to the command line options with "--initialize" requiring a destination directory.
   Raise exceptions if the destination directory has files that would be overwritten.

# install the *pv2web_ro* package into your Python environment
# initialize the project configuration directory
# identify the web server directory to be used
# edit config.xml
# identify the list of EPICS PVs
# edit pvlist.xml
# customize the livedata display file: edit livedata.xsl
# run the config.xml file (in the background)::
  
  pv2web_ro config.xml &
  
# watch the log_data.txt file in the project directory

.. toctree::
   :maxdepth: 2
   :glob:

   install
   init
   pvlist
   config
   manage
