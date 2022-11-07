"""
pvWebMonitor
"""

__package_name__ = "pvWebMonitor"
__description__ = "Create static web site from EPICS PVs."
__long_description__ = __description__
__author__ = "Pete R. Jemian"
__email__ = "jemian@anl.gov"
__institution__ = "Advanced Photon Source, Argonne National Laboratory"
__author_name__ = __author__
__author_email__ = __email__

__copyright__ = "2005-2020, UChicago Argonne, LLC"
# __license_url__         = u''
__license__ = "UChicago Argonne, LLC OPEN SOURCE LICENSE (see LICENSE file)"
__url__ = "http://pvWebMonitor.readthedocs.io"
__download_url__ = "https://github.com/prjemian/pvWebMonitor.git"
__keywords__ = ["EPICS", "PV", "tool", "HTML"]
__requires__ = ["pyepics", "lxml", "numpy", "ophyd"]

__classifiers__ = [
    "Development Status :: 6 - Mature",
    "Environment :: Console",
    "Environment :: Web Environment",
    "Intended Audience :: Science/Research",
    "License :: Free To Use But Restricted",
    "Operating System :: OS Independent",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
    "Programming Language :: Python :: 3.10",
    "Topic :: Scientific/Engineering",
    "Topic :: Software Development :: Embedded Systems",
    "Topic :: Software Development :: Libraries :: Python Modules",
    "Topic :: Utilities",
]

# as shown in the About box ...
__credits__ = "\n".join(
    [
        f"author: {__author__}",
        f"email: {__email__}",
        f"institution: {__institution__}",
        f"UR: {__url__}",
    ]
)

from ._version import get_versions

__version__ = get_versions()["version"]
del get_versions
__release__ = __version__
