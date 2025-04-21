Installation
============

If you need to install the *pvWebMonitor* package::

   pip install pvWebMonitor

To install for development, follow these terse instructions:

.. code-block:: bash
   :linenos:

   git clone https://github.com/BCDA-APS/pvWebMonitor.git
   cd pvWebMonitor
   ENV_NAME=pvWebMonitor
   conda create -y -n "${ENV_NAME}" "python=3.13" pandoc
   conda activate "${ENV_NAME}"
   pip install -e .

Once the installation is complete,
the *pvWebMonitor* executable should be ready to use.
