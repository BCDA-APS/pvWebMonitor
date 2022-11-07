.. _config_file:

=====================
The `config.xml` file
=====================

The *config.xml* file defines constants needed by the program.

Definitions for each item listed in the table 
under :meth:`pvWebMonitor.read_config.read_xml`
are provided, such as this example:

   .. compound::
   
      .. rubric:: Example ``config.xml`` file.
      
      .. literalinclude:: ../../../src/pvWebMonitor/project/config.xml
         :tab-width: 4
         :linenos:
         :language: guess

To use the *pvWebMonitor* service effectively, it is likely
you will only need to edit the value for *LOCAL_WWW_LIVEDATA_DIR*
which defines the location of the directory used by the web server
to serve content.

Preamble
--------

The *config.xml* must be "well-formed XML".  

The first line of the file is *always*:

.. code-block:: guess
   :linenos:

   <?xml version="1.0" ?>

This line declares this to be a file that should be well-formed XML
according to the version 1.0 standard.  

Root Tag
--------

All well-formed XML files have a single element at the outermost (root) 
level of the file.  In the *config.xml* file, the root element
is **pvWebMonitor__config**.  Note the closing ``</pvWebMonitor__config>`` 
tag at the end of the file.

A version attribute describes this file adheres to the ``version="1.0"``
definition of *config.xml* files.  That definition is described in the
XML Schema file *config.xsd* provided in the source code package.

This XML Schema definition is used to validate the *config.xml* when it is read.
If there are problems, the first problem discovered will be reported.
