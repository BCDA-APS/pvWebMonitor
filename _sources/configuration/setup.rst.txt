=============================
Setup a new project directory
=============================

The *pvWebMonitor* service is configured by files
configured by the user in a *project directory*.

To get default versions of the files, run this command::

   mkdir path/to/project/directory
   pvWebMonitor --setup path/to/project/directory
   cd path/to/project/directory

where *path/to/project/directory* is either a partial, relative,
or absolute path to an existing directory to be used.  Once this 
command has run, the files will be copied to the designated
directory.  If files with these names already exist, *pvWebMonitor*
will stop with an error report and not overwrite the existing files.

===============  ============================================
file             How is it used?
===============  ============================================
config.xml       defines user settings for the program
pvlist.xml       declares list of EPICS PVs to be monitored
pvlist.xsl       for easy display of pvlist.xml
livedata.xsl     user-customized display
rawdata.xsl      standard display of all monitored EPICS PVs
manage.sh        shell script to manage the background task
===============  ============================================

Each of these files will be explained in the coming sections.
