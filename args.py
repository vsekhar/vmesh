import os
import ConfigParser
from cStringIO import StringIO
from sys import argv
from argparse import ArgumentParser, SUPPRESS
from ast import literal_eval

# create safe argv (for logging, etc.)
hidden_arguments = set(['--access-key', '--secret-key'])
def hider(x):
	for arg in hidden_arguments:
		if x.startswith(arg):
			return x.partition('=')[0] + '=[hidden]'
	return x
safeargv = list(map(hider, argv))

# parse command line
parser = ArgumentParser(description='vmesh-launch.py: initial package script')
parser.add_argument('--access-key', type=str, help='access key')
parser.add_argument('--secret-key', type=str, help='secret key')
parser.add_argument('-c', '--config-file', type=str, help='config file (default=\'config\')')
parser.add_argument('-l', '--local', default=False, action='store_true', help='run in local/debug mode (no AWS metadata, implies --interactive)')
parser.add_argument('-i', '--interactive', default=False, action='store_true', help='interactive (don\' redirect console to logfile)')
parser.add_argument('--list', default=False, action='store_true', help='list hosts and exit (do not register this host)')
parser.add_argument('-r', '--reset', default=False, action='store_true', help='reset metadata at startup')
parser.add_argument('-d', '--debug', default=SUPPRESS, action='store_true', help='debug (print more output)')
parser.add_argument('--log', type=str, default=SUPPRESS, help='log file')
parsed_args = parser.parse_args()

if parsed_args.local:
	parsed_args.interactive = True

if not parsed_args.config_file:
	if __name__ == '__main__':
		parsed_args.config_file = os.path.join(os.getcwd(), 'config')
	else:
		parsed_args.config_file = os.path.join(os.path.dirname(__file__), 'config')

config_current_version = 0
config_latest_version = 0

def new_config_available(new_version):
	""" Register that a new config is available (monotonically increasing version number) """
	global config_current_version, config_latest_version
	if new_version > config_current_version and new_version > config_latest_version: 
		config_latest_version = new_version
		return True
	return False

def update_config(data, version, initial=False):
	global config, config_current_version, config_latest_version
	if initial or version > config_current_version:
		try:
			new_config = ConfigParser.SafeConfigParser()
			new_config.readfp(StringIO(data))
			config = new_config
			config_current_version = version
		except ConfigParser.Error:
			# stop trying to load this config (attempts are restarted after polling interval)
			config_latest_version = config_current_version

			from logger import log # must be deferred b/c logger uses args
			log.warning('Error loading config version %d, reverting to config version %d' % (version, config_current_version))
		else:
			# update if greater than latest version ever seen
			config_latest_version = max(version, config_latest_version)

initial_config_data = ''.join(open(parsed_args.config_file, 'rt').readlines())
update_config(data=initial_config_data, version=0, initial=True)

# combined getter
def get(name, section=None):
	global parsed_args, config
	try:
		return getattr(parsed_args, name) # command-line overrides configuration
	except AttributeError:
		return literal_eval(config.get(section or 'vmesh', name))

def get_kernel(name):
	return get(name, 'kernel')

