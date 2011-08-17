#!/usr/bin/python

__author__ = 'Vivek Sekhar'

import sys
from setuptools import setup, find_packages

setup_args = dict(
		name='vmesh',
		version='0.1',
		author=__author__,
		author_email='vivek@viveksekhar.ca',
		packages=['vmesh', 'vpush', 'twisted.plugins'],
		package_data={'twisted': ['plugins/vmesh_plugin.py'],
					'vmesh': ['config'],
					'vpush': ['cvpush.so']},
		zip_safe=False
		)

if sys.version_info[:2] >= (2, 4):
	setup_args['classifiers']=[
			"Development Status :: 2 - Pre-Alpha",
			"Environment :: No Input/Output (Daemon)",
			"Intended Audience :: Science/Research",
			"License :: OSI Approved :: GNU General Public License (GPL)",
			"Operating System :: POSIX :: Linux",
			"Programming Language :: Python :: 2.7",
			"Topic :: Scientific/Engineering :: Artificial Intelligence"
		]

def run():
	return setup(**setup_args)

if __name__ == '__main__':
	run()

	# refresh plugin cache
	# from twisted.plugin import IPlugin, getPlugins
	# list(getPlugins(IPlugin))

