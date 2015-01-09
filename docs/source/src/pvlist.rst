The `pvlist.xml` file
=====================

.. note:: tba

The complete list of EPICS Process Variables to be monitored
is declared in the `pvlist.xml` file.  An example of such a 
file is shown below. 

   .. compound::
   
      .. rubric:: Example `pvlist.xml` file.
         You can edit this file with a text editor.
      
      .. literalinclude:: pvlist.xml
         :tab-width: 4
         :linenos:
         :language: guess

.. explain the example

.. explain how to comment out PV declarations
   _ignore_ attribute
   wrap in XML comment

==============    ==============================================================================
attribute         definition
==============    ==============================================================================
mne               one-word mnemonic reference used in python and xslt code
                  (mne should be unique for each EPICS_PV)
PV                EPICS process variable name (must be used in only one EPICS_PV)
description       useful text informative to others
display_format    (optional, default="%s") PVs will be formatted for display with this string
_ignore_          (optional, default="false") this PV is ignored if value is not "false"
==============    ==============================================================================


These two declarations are equivalent:

.. code-block:: guess
   :linenos:
   
   <EPICS_PV PV="ioc:xps:c0:m1.RBV" description="motor MR, degrees" display_format="%.6f" mne="mr"/>

.. code-block:: guess
   :linenos:
   
   <EPICS_PV
     PV="ioc:xps:c0:m1.RBV" 
     description="motor MR, degrees" 
     display_format="%.6f" 
     mne="mr"
     />
   


