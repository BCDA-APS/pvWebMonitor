"""pvWebMonitor"""

__package_name__ = "pvWebMonitor"

try:
    from setuptools_scm import get_version

    __version__ = get_version(root="..", relative_to=__file__)
    del get_version
except (LookupError, ModuleNotFoundError):
    from importlib.metadata import version

    __version__ = version(__package_name__)
    del version

# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2005-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
