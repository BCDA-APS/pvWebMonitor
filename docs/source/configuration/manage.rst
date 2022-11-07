The `manage.sh` file
====================

The ``pvWebMonitor`` may be run as either a command-line program or run in a
background (daemon) process.  To ensure the program is always as intended, a
shell script is used to initialize and/or restart as needed.  The shell script
may be called periodically by a system scheduler such as :ref:`cron`. An
example shows the shell script installed with a new project directory.  The
contents of the file are described below.

The shell script is run with either of these commands:

======================  ================================================================== 
command                 description
======================  ================================================================== 
``manage.sh help``      Short text showing these commands.
``manage.sh start``     Starts a process and writes the *pid* to the ``PIDFILE``.
``manage.sh stop``      Stops the process with *pid* matching value in the ``PIDFILE``.
``manage.sh restart``   Stops, then starts the process (in the background).
``manage.sh checkup``   Checks if the process is running.  Starts it if it is not running.
======================  ================================================================== 

.. compound::

   .. rubric:: Example shell script

   Example shell script to manage the ``pvWebMonitor``
   process either as a startup or a background daemon.

   .. literalinclude:: ../../../src/pvWebMonitor/project/manage.sh
      :tab-width: 4
      :linenos:
      :language: guess

``PROJECT_DIR``:
   The local directory for the configuration files used by the ``pvWebMonitor``
   process. You probably want to change this.  All other files are relative to
   the ``${PROJECT_DIR}``.
``CONFIG_FILE``:
   The configuration file used by the ``pvWebMonitor`` process. You probably
   want to change this.  See the :ref:`config_file` section.
``EXECUTABLE_SCRIPT``:
   The absolute path to the ``pvWebMonitor`` code. You probably do not need to
   change this.
``LOGFILE``:
   Any information logged by the ``pvWebMonitor`` process will be written
   to this file.  It is not necessary for you to change this value.
``PIDFILE``:
   This file contains the current system process identifier (*pid*)
   of the ``pvWebMonitor`` process.  Do not change this file.
``RETVAL``:
   Internal use.  Do not change this.

.. _cron:

cron - The Linux system scheduler
-----------------------------------------

Linux has a system task scheduler called ``cron``.  (see, for example
https://opensource.com/article/17/11/how-use-cron-linux) This may be used to run
periodic processes or to run processes at certain times (such as on system
startup).  You edit your ``cron`` file and add or modify the configuration
lines for your periodic command.

.. tip:: Be sure to redirect the output  or you'll get lots of email from ``cron``!

Here, we use ``cron`` to both start ``pvWebMonitor`` on system startup and to
check up on it to ensure it stays running by running the ``manage.sh checkup``
command periodically.  The logic is the period between calls is the time we choose to wait 
between checkups.  Either on system startup or a restart of the process, this will be the
longest time that the process is not running.

To edit your ``cron`` file, type ``crontab -e`` on the linux command line.  (You
might be asked to choose your text editor.)  Paste these lines into the editor
(usually at the bottom):

.. code-block::

   # every five minutes (redirect cron output to ignore)
   */5 * * * *  /tmp/pv/manage.sh checkup 2>&1 >> /dev/null

The syntax of the file is described in ``cron``'s documentation.
Suffice to say this runs the ``manage.sh checkup`` command (from the ``/tmp/pv``
directory -- change to where your ``${PROJECT_DIR}`` directory is located).
It runs all day, every day, every 5 minutes, starting at :00, :05, :10, ...
