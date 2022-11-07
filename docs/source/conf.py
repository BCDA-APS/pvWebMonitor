# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

import sys, pathlib

sys.path.insert(
    0, str(pathlib.Path(__file__).parent.parent / "src")
)
import pvWebMonitor


project = pvWebMonitor.__package_name__
copyright = pvWebMonitor.__copyright__
author = 'Pete Jemian'
version = pvWebMonitor.__version__
release = pvWebMonitor.__release__


# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = """
    sphinx.ext.autodoc
    sphinx.ext.autosummary
    sphinx.ext.coverage
    sphinx.ext.githubpages
    sphinx.ext.inheritance_diagram
    sphinx.ext.mathjax
    sphinx.ext.todo
    sphinx.ext.viewcode

""".split()

templates_path = ['_templates']
exclude_patterns = []
source_suffix = '.rst'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_static_path = ['_static']
html_theme = "pydata_sphinx_theme"

autodoc_mock_imports = pvWebMonitor.__requires__
