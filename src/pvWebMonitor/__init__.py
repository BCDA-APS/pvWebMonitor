"""pvWebMonitor"""

__package_name__ = "pvWebMonitor"
__settings_orgName__ = "BCDA-APS"


def _get_version():
    """Make the version code testable."""
    import importlib.metadata
    import importlib.util

    text = importlib.metadata.version(__package_name__)

    if importlib.util.find_spec("setuptools_scm") is not None:
        """Preferred source of package version information."""
        import setuptools_scm

        try:
            text = setuptools_scm.get_version(root="..", relative_to=__file__)
        except LookupError:
            pass

    return text


__version__ = _get_version()

# -----------------------------------------------------------------------------
# :author:    BCDA
# :copyright: (c) 2005-2025, UChicago Argonne, LLC
#
# Distributed under the terms of the Argonne National Laboratory Open Source License.
#
# The full license is in the file LICENSE.txt, distributed with this software.
# -----------------------------------------------------------------------------
