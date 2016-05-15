
'''
pvWebMonitor
'''

__package_name__        = u'pvWebMonitor'
__description__         = u'post EPICS PVs to read-only web page'
__long_description__    = __description__

#__version__             = u'2016.0427.1'
#__release__             = __version__
__author__              = u'Pete R. Jemian'
__email__               = u'jemian@anl.gov'
__institution__         = u"Advanced Photon Source, Argonne National Laboratory"
__author_name__         = __author__
__author_email__        = __email__

__copyright__           = u'2005-2016, UChicago Argonne, LLC'
# __license_url__         = u''
__license__             = u'UChicago Argonne, LLC OPEN SOURCE LICENSE (see LICENSE file)'
__url__                 = u'http://pvWebMonitor.readthedocs.org'
__download_url__        = u'https://github.com/prjemian/pvWebMonitor.git'
__keywords__            = ['EPICS', 'PV', 'tool', 'HTML']
__requires__            = ['pyepics', 'lxml', 'numpy']

__classifiers__ = [
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Environment :: Web Environment',
            'Intended Audience :: Science/Research',
            'License :: Free To Use But Restricted',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Scientific/Engineering',
            'Topic :: Software Development :: Embedded Systems',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Utilities',
                     ]

# as shown in the About box ...
__credits__ = u'author: ' + __author__
__credits__ += u'\nemail: ' + __email__
__credits__ += u'\ninstitution: ' + __institution__
__credits__ += u'\nURL: ' + __url__


import os
on_rtd = os.environ.get('READTHEDOCS', None) == 'True'
from _version import get_versions
__version__ = get_versions()['version']
del get_versions
if on_rtd:
    # special handling for readthedocs.org, remove distracting info
    __version__ = __version__.split('+')[0]
__release__   = __version__
