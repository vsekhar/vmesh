
import sys
import os
import argparse
from ast import literal_eval as parse
import ConfigParser
from ConfigParser import NoOptionError, NoSectionError

# command line
parser = argparse.ArgumentParser(description='cloudlaunch.py: launch scripts in the cloud')
parser.add_argument('-l', '--local', default=False, action='store_true', help='run locally')
parser.add_argument('-d', '--debug', default=argparse.SUPPRESS, action='store_true', help='run in debug mode (more output)')
parser.add_argument('-b', '--bare', default=argparse.SUPPRESS, action='store_true', help='launch bare instances only (no initial config)')
parser.add_argument('--config-only', default=False, action='store_true', help='merge and output config file, then exit')
parser.add_argument('-u', '--upload-only', default=False, action='store_true', help='upload the package, then exit')
parser.add_argument('-f', '--config-file', default=None, help='config file to use (default=\'~/.vmesh\')')
parser.add_argument('-c', '--configuration', default='DEFAULT', help='configuration name in config file (default=\'DEFAULT\')')
parser.add_argument('--list-configurations', default=False, action='store_true', help='list configurations, then exit')
parser.add_argument('-n', '--count', default=argparse.SUPPRESS, help='number of nodes to start')
_args = parser.parse_args()

# binary arguments (arguments that can appear in the commandline or config) and their defaults
bin_defs = [('debug', False), ('bare', False), ('count', 1)]

# configuration file
if not _args.config_file:
	homedir = os.getenv('USERPROFILE') or os.getenv('HOME')
	_args.config_file = os.path.join(homedir, '.vmesh')

config = ConfigParser.SafeConfigParser()
config.read(_args.config_file)

# handle inheritance
inherit_processed = set()

def process_inheritance(section):
	inherit_processed.add(section)

	# does it inherit anything?
	if config.has_option(section, 'inherit'):
		src = parse(config.get(section, 'inherit'))
		if src == section:
			print 'Warning: recursive inheritance of section \'%s\'' % section

		# recurse if needed
		if src not in inherit_processed:
			process_inheritance(src)

		# process current section
		cur_values = list(config.items(section)) # stash (dest overrides src)
		for name, value in config.items(src):
			config.set(section, name, value) # get source values
		for name, value in cur_values:
			config.set(section, name, value) # restore overrides

for section in config.sections():
	process_inheritance(section)

# combined getter (defaults to active configuration, unless a section is specified)
def get(name, section=None):
	""" Argument getter (combines command-line and config file, with command-line
		taking precedence) """
	global _args
	try:
		return getattr(_args, name) # command-line overrides configuration file
	except AttributeError:
		global config
		return parse(config.get(section or _args.configuration, name))

for arg, default in bin_defs:
	try:
		get(arg)
	except NoOptionError:
		setattr(_args, arg, default)

