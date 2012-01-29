#!/usr/bin/python

__author__ = 'Vivek Sekhar'
__author_email__ = 'vivek@viveksekhar.ca'

try:
	from setuptools import setup
except ImportError:
	from distutils.core import setup

import sys

from vmesh import __version__

if sys.version_info <= (2, 6):
	error = "ERROR: vmesh requires Python version 2.6 or above... exiting"
	print >> sys.stderr, error
	sys.exit(1)

setup_args = dict(
		name = 'vmesh'
		, description = 'Mesh computation library'
		, version = __version__
		, author = __author__
		, author_email = __author_email__
		, packages=['vmesh', 'vpush', 'twisted.plugins']
		, package_data={'twisted': ['plugins/vmesh_plugin.py']
					#, 'vmesh': ['config'] # necessary?
					#, 'vpush': ['cvpush.so']
					}
		, zip_safe=False
		)

if sys.version_info[:2] >= (2, 4):
	setup_args['classifiers']=[
			"Development Status :: 2 - Pre-Alpha"
			, "Environment :: No Input/Output (Daemon)"
			, "Intended Audience :: Science/Research"
			, "License :: OSI Approved :: GNU General Public License (GPL)"
			, "Operating System :: POSIX :: Linux"
			, "Programming Language :: Python :: 2.7"
			, "Topic :: Scientific/Engineering :: Artificial Intelligence"
		]

def run():
	return setup(**setup_args)

if __name__ == '__main__':
	run()

	# refresh plugin cache
	# from twisted.plugin import IPlugin, getPlugins
	# list(getPlugins(IPlugin))

