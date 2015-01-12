#!/bin/tcsh
#
# chkconfig: - 98 98
# description: pv2web_ro WWW page update script for IOC: prj
#
# processname: pv2web_ro_update

setenv SCRIPT_DIR	 /home/oxygen18/JEMIAN/Documents/eclipse/pv2web_ro/src/pv2web_ro
setenv MANAGE		 ${SCRIPT_DIR}/manage.csh
setenv WWW_DIR		 ${SCRIPT_DIR}/localwww
setenv SCRIPT		 ${SCRIPT_DIR}/main.py
setenv LOGFILE		 ${WWW_DIR}/log.txt
setenv PIDFILE		 ${WWW_DIR}/pid.txt
setenv PYTHON		 /home/oxygen/JEMIAN/Apps/anaconda/bin/python
setenv CAGET		 /APSshare/epics/extensions-base/3.14.12.3-ext1/bin/linux-x86_64/caget


switch ($1)
  case "start":
       cd ${SCRIPT_DIR}
       ${PYTHON} ${SCRIPT} >>& ${LOGFILE} &
       setenv PID $!
       /bin/echo ${PID} >! ${PIDFILE}
       /bin/echo "# [$0 `/bin/date`] started ${PID}: ${SCRIPT}"
       breaksw
  case "stop":
       cd ${SCRIPT_DIR}
       setenv PID `/bin/cat ${PIDFILE}`
       # get the full list of PID children
       # this line browses pstree and strips non-numbers
       set pidlist=`pstree -p $PID | tr -c "[:digit:]"  " " `
       /bin/ps ${PID} >! /dev/null
       setenv NOT_EXISTS $?
       if (${NOT_EXISTS}) then
            /bin/echo "# not running ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
       else
            kill ${PID}
            /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
            /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}"
       endif
       # the python code starts a 2nd PID which also needs to be stopped
       setenv PID `expr "${pidlist}" : '[0-9]*\( [0-9]*\)'`
       /bin/ps ${PID} >! /dev/null
       setenv NOT_EXISTS $?
       if (${NOT_EXISTS}) then
            /bin/echo "# [$0 `/bin/date`] not running ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
       else
            if (${PID} != "") then
		 kill ${PID}
 		 /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}" >>& ${LOGFILE} &
 		 /bin/echo "# [$0 `/bin/date`] stopped ${PID}: ${SCRIPT}"
	    endif
       endif
       breaksw
  case "restart":
       $0 stop
       $0 start
       breaksw
  case "checkup":
       #=====================
       # call periodically (every 5 minutes) to see if livedata is running
       #=====================
       #	field	       allowed values
       #      -----	     --------------
       #      minute	     0-59
       #      hour	     0-23
       #      day of month   1-31
       #      month	     1-12 (or names, see below)
       #      day of week    0-7 (0 or 7 is Sun, or use names)
       #
       # */5 * * * * /home/beams/S15USAXS/Documents/eclipse/USAXS/livedata/manage.csh checkup 2>&1 /dev/null
       #
       # 2013-10-25,prj: new cleanup part, until pvwatch.py starts getting it right again
       /bin/rm -f /tmp/tmp*.p*
       #
       set pid = `/bin/cat ${PIDFILE}`
       setenv RESPONSE `ps -p ${pid} -o comm=`
       if (${RESPONSE} != "python") then
          echo "# [$0 `/bin/date`] could not identify running process ${pid}, restarting" >>& ${LOGFILE}
	  # swallow up any console output
          echo `${MANAGE} restart` >& /dev/null
       else
 	  # look to see if the process has stalled, then restart it
 	  echo "# [$0 `/bin/date`] process ${pid} appears stalled, restarting" >>& ${LOGFILE}
	  # swallow up any console output
 	  echo `${MANAGE} restart` >& /dev/null
       endif
       breaksw
  default:
       /bin/echo "Usage: $0 {start|stop|restart|checkup}"
       breaksw
endsw
