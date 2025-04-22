Overview
########

The basic flow of data from EPICS to the static web site is described in the
following diagram:

.. figure:: _static/overview.jpg
      :width: 90%
      
      flow of data from EPICS to WWW site

The **pvWebMonitor** service is run on a computer in the same subnet 
as the EPICS system to be monitored.  
All configuration files and other resources are placed in a single 
:index:`project directory`. **pvWebMonitor** places an EPICS Channel 
Access monitor on each PV in the *pvlist.xml* file and stores updates 
in-memory.  
Periodically, as specified in *config.xml*, **pvWebMonitor** writes 
the PV values from memory to an XML file (named *rawdata.xml*) in the 
project directory. 
Once that XML file is written, **pvWebMonitor** uses *rawdata.xml* 
[#]_ with each of the XSLT files [#]_ in the project directory to 
create a corresponding HTML file in the project directory.  
The complete list of HTML files is written into an *index.html* file 
in the project directory. 
Finally, all content in the project directory (except for the 
*config.xml* file) is copied to the WWW site directory.  (Only new 
content is copied, files that do not change are not re-copied.) 

It is important to note the WWW site is written as a *static web site* 
so that it provides no opportunity to change any value in the EPICS system 
being monitored.

Also, since some browsers do not have XML parsers and thus cannot render XSLT [#]_,
all HTML files are created by **pvWebMonitor**.

.. [#] The *rawdata.xml* file contains all the EPICS PV values, as well as 
   some additional metadata useful in building the WWW site.

.. [#] Each XSLT files (``*.xsl``) contains the layout of a single HTML page,
   with additional markup to display the current EPICS PV values (and metadata).
   The EPICS PV data is provided in *rawdata.xml*.
   
.. [#] https://www.w3schools.com/xml/xsl_intro.asp

Examples
********

Example (very brief [#]_) *rawdata.xml* file:

.. literalinclude:: short.xml
    :tab-width: 4
    :linenos:
    :language: xml


Each XSLT file describes the format of an HTML page.
The XSLT file uses XSL markup to pick EPICS PV values from the XML file.
Here's an example that shows the value of the PV ``prj:m1.RBV``.
(The *id* ``VDM_Stripe`` is used here as a symbolic reference.):

.. code-block:: xml

  <xsl:value-of select="//pv[@id='VDM_Stripe']/value"/>

Here's how to show when that PV value was last updated:

.. code-block:: xml

  <xsl:value-of select="//pv[@id='VDM_Stripe']/timestamp"/>

Here's how to show when the EPICS PV data was last posted to the WWW site:

.. code-block:: xml

  <xsl:value-of select="/pvWebMonitor/datetime"/>

The XSLT language has many additional functions available to help
as your page designs get more complex.  Look at the supplied *livedata.xsl*
file for additional examples.  There are good tutorial web sites available,
such as:  http://www.w3schools.com/xsl

Here's an example XSLT file using these example lines above (line breaks,
``<br />``, were added for clarity):

.. literalinclude:: short.xsl
    :tab-width: 4
    :linenos:
    :language: xml

The XSLT transformation using the XML file above looks like:

.. literalinclude:: short.html
    :tab-width: 4
    :linenos:
    :language: xml

Which shows in a browser:

.. figure:: short.jpg
      
      Example HTML web page from above.


.. [#] A more complete example is provided in the :ref:`example` section.
