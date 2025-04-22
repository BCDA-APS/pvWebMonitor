.. This page did not publish on GitHub when it was named without
   the trailing underscore.
   https://github.com/BCDA-APS/pvWebMonitor/issues/52

The `pvlist.xml` file
#####################

The complete list of EPICS Process Variables to be monitored
is declared in the *pvlist.xml* file.  

Preamble
********

The *pvlist.xml* must be "well-formed XML".  
(Google for this term to become informed what this means.)

The first lines of the file are *always*:

.. code-block:: xml
   :linenos:

   <?xml version="1.0" ?>
   <?xml-stylesheet type="text/xsl" href="pvlist.xsl" ?>

The first line declares this to be a file that should be well-formed XML
according to the version 1.0 standard.  The second line provides a
convenience definition for visualizing the *pvlist.xml* file in a
browser that uses the *pvlist.xsl* file to format the XML content
into something that humans can more easily read.  To do this, the
*pvlist.xsl* file must be in the same directory as the *pvlist.xml* file.

Root tag
********

All well-formed XML files have a single element at the outermost (root) 
level of the file.  In the *pvlist.xml* file, the root element
is **pvwatch**.  Note the closing ``</pvwatch>`` tag at the end of the file.

A version attribute describes this file adheres to the ``version="1.0"``
definition of *pvlist.xml* files.  That definition is described in the
XML Schema file *pvlist.xsd* provided in the source code package.

This XML Schema definition is used to validate the *pvlist.xml* when it is read.
If there are problems, the first problem discovered will be reported.

Inside the root tag, *EPICS_PV* elements describe the PVs to be monitored.
Additionally, *definition* tags are provided to describe the terms used.

Describe a PV to Monitor
************************

Each PV to be monitored is declared in the XML file using
a line such as this example:

.. code-block:: xml
   :linenos:
   
   <EPICS_PV
     PV="ioc:xps:c0:m1.RBV" 
     mne="mr"
     description="motor MR, degrees" 
     />

This says to monitor the EPICS process variable named
``ioc:xps:c0:m1.RBV`` and to associate that value with
the mnemonic named ``mr``.  The description text
``motor MR, degrees`` can be used in displays for this value.
The tag ``EPICS_PV`` describes this as a PV declaration.
It must appear in uppercase letters.
A complete list of terms is described in the section below: 
`ref`:pvlist.terms`.

At minimum, it is required to provide the *PV*, *mne*,
and *description* attributes.

The order of the attributes is not important, they can be given in any order.
Also, the spacing between attributes is not important.  The entire
*EPICS_PV* element can be specified on one line or broken across several lines.

Keep the description text short. Longer descriptions, including
those with line breaks, are less useful in creating display screens.

.. see: https://stackoverflow.com/questions/1631396/what-is-an-xsncname-type-and-when-should-it-be-used

**Note:** The mnemonic name ``mne`` must adhere to the rules for XML ``NCName`` (non-colonized name).  
The practical restrictions of NCName are that it cannot contain several 
symbol characters like 
``:``, ``@``, ``$``, ``%``, ``&``, ``/``, ``+``, ``,``, ``;``, 
whitespace characters or different parentheses. 
Furthermore an NCName cannot begin with a 
number, dot or minus character although they can appear later in an NCName.
The regular expression is:  ``[\i-[:]][\c-[:]]*``


The closing tag
===============

Note that ``/>`` is used to close the ``EPICS_PV`` element.
It is equivalent to use:

.. code-block:: xml
   :linenos:
   
   <EPICS_PV
     PV="ioc:xps:c0:m1.RBV" 
     mne="mr"
     description="motor MR, degrees" 
     ></EPICS_PV>

but this is not advised since no content is allowed for
EPICS_PV elements, only attributes.


.. _pvlist.terms:

Terms
*****

==============    ==============================================================================
attribute         definition
==============    ==============================================================================
mne               one-word mnemonic reference used in python and xslt code
                  (mne should be unique for each EPICS_PV)
PV                EPICS process variable name (must be used in only one EPICS_PV)
description       useful text informative to others
display_format    (optional, default="%s") PVs will be formatted for display with this string
_ignore_          (optional, default="false") this PV is ignored if value is not "false"
as_string         (optional, default="false") whether to return the string representation of the value
==============    ==============================================================================


These two declarations are equivalent:

.. code-block:: xml
   :linenos:
   
   <EPICS_PV PV="ioc:xps:c0:m1.RBV" description="motor MR, degrees" display_format="%.6f" mne="mr"/>

.. code-block:: xml
   :linenos:
   
   <EPICS_PV
     PV="ioc:xps:c0:m1.RBV" 
     description="motor MR, degrees" 
     display_format="%.6f" 
     mne="mr"
     />


.. index:: as_string

EPICS R3 strings using the *waveform* record (``as_string``)
************************************************************

In EPICS R3 IOCs, it is common to provide support for long strings (40 or more characters)
using a :index:`waveform` [#]_ record with character data type.  For example, the EPICS 
:index:`AreaDetector` [#]_ has such a PV to store the full path (length up to 256) to an attributes file. 
Here's an example using the PV with an instance of the :index:`ADSimDetector` [#]_::

   $ caget 13SIM1:cam1:NDAttributesFile.{RTYP,FTVL,VAL}
   13SIM1:cam1:NDAttributesFile.RTYP waveform
   13SIM1:cam1:NDAttributesFile.FTVL CHAR
   13SIM1:cam1:NDAttributesFile.VAL 256 47 116 109 112 47 ...

`pvWebMonitor` uses the ``as_string`` support from PyEpics [#]_ to report
both the character list values and the text string values of the string waveform.
Here is the configuration in `pvlist.xml` to watch that PV::

    <EPICS_PV 
        PV="13SIM1:cam1:NDAttributesFile"  
        description="NDAttributesFile array"  
        mne="NDAttributesFile_array"/>

and here is typical content in the `rawdata.xml` file::

   <pv id="NDAttributesFile_array" name="13SIM1:cam1:NDAttributesFile">
      <name>13SIM1:cam1:NDAttributesFile</name>
      <id>NDAttributesFile_array</id>
      <description>NDAttributesFile array</description>
      <timestamp>2017-12-11 11:09:43.157445</timestamp>
      <record_type>waveform</record_type>
      <counter>2</counter>
      <units></units>
      <value>[ 47 116 109 112  47  97 116 116 114 105  98 117 116 101 115  46 120 109 108   0]</value>
      <char_value>/tmp/attributes.xml</char_value>
      <raw_value>[ 47 116 109 112  47  97 116 116 114 105  98 117 116 101 115  46 120 109 108   0]</raw_value>
      <format>%s</format>
   </pv>
   
You'll need to access the text as a string using ``char_value`` rather than just ``value``.
If you want the ``value`` to be the text string, add the ``as_string="true"`` 
attribute in the entry in the `pvlist.xml` file, such as::

    <EPICS_PV 
        PV="13SIM1:cam1:NDAttributesFile"  
        description="NDAttributesFile array"  
        mne="NDAttributesFile_array"
        as_string="true"/>

Then, the ``char_value`` and the ``value`` both have the string as a result::

   <pv id="NDAttributesFile_string" name="13SIM1:cam1:NDAttributesFile">
      <name>13SIM1:cam1:NDAttributesFile</name>
      <id>NDAttributesFile_string</id>
      <description>NDAttributesFile string</description>
      <timestamp>2017-12-11 11:09:43.185298</timestamp>
      <record_type>waveform</record_type>
      <counter>2</counter>
      <units></units>
      <value>/tmp/attributes.xml</value>
      <char_value>/tmp/attributes.xml</char_value>
      <raw_value>[ 47 116 109 112  47  97 116 116 114 105  98 117 116 101 115  46 120 109 108   0]</raw_value>
      <format>%s</format>
   </pv>

In both cases, whether or not ``as_string`` is used, the character list representation
is available in the ``raw_value`` and the text string representation is available
in the ``char_value``.

.. [#] EPICS R3 *waveform* record: 
       https://wiki-ext.aps.anl.gov/epics/index.php/RRM_3-14_Waveform
.. [#] EPICS AreaDetector: 
       http://cars9.uchicago.edu/software/epics/areaDetector.html
.. [#] ADSimDetector: 
       http://cars.uchicago.edu/software/epics/simDetectorDoc.html
.. [#] PyEpics:
       http://cars9.uchicago.edu/software/python/pyepics3/pv.html?highlight=as_string#pv.get


Removing declarations
*********************

Sometimes, it is necessary to stop watching a certain PV.
There are three ways to do this.   It can be commented out
using XML comments, it can be marked to *_ignore_* it,
or the declaration could be deleted.  We'll describe the 
first two cases.

Comment out in XML
==================

To comment out using an XML comment (``<!-- -->``),
take this code:

.. code-block:: xml
   :linenos:
   
   <EPICS_PV PV="ioc:m1" mne="m1" description="motor 1" />

and surround it with XML comment tags, such as:

.. code-block:: xml
   :linenos:
   
   <!--
   <EPICS_PV PV="ioc:m1" mne="m1" description="motor 1" />
   -->

XML comment tags can be used to block out many *EPICS_PV*
declarations at once.

Marking with *_ignore_* attribute
=================================

To mark a single *EPICS_PV* declaration to be ignored,
take this code:

.. code-block:: xml
   :linenos:
   
   <EPICS_PV PV="ioc:m1" mne="m1" description="motor 1" />

and add the ``_ignore_="true"`` attribute, such as:

.. code-block:: xml
   :linenos:
   
   <EPICS_PV _ignore_="true" PV="ioc:m1" mne="m1" description="motor 1" />

The *_ignore_* attribute can be given in any order.  The value *true* may be
upper or lower case but must be enclosed by double quotes.

Each PV to be ignored using the *_ignore_* attribute must
have its own *_ignore_* attribute.  You cannot mark a whole block
of *EPICS_PV* elements with a single *_ignore_* attribute.

Example *pvlist.xml* file
*************************
An example of such a file is shown below. 

   .. compound::
   
      .. rubric:: Example `pvlist.xml` file.
         You can edit this file with a text editor.
      
      .. literalinclude:: pvlist.xml
         :tab-width: 4
         :linenos:
         :language: xml
