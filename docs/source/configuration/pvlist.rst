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
