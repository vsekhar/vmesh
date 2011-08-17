import ConfigParser
from cStringIO import StringIO

from twisted.python import usage

###############################################################################
# Options definition (passed via tap to twistd)
###############################################################################

class BaseOptions(usage.Options):
	""" Options for all sub-commands """
	optFlags = [['debug', 'd', 'Debug mode']
				,['local', 'l', 'Local mode']
				,['interactive', 'i', 'Interactive mode (implies --local)']
				]

class Options(BaseOptions):
	subCommands = [['list-peers', None, None, 'List peers in DB and exit']
					, ['reset', 'r', None, 'Reset metadata and exit']
					]

	optParameters = [['config-file', 'c', None, 'Configuration file to load']
					, ['port', 'p', 0, 'The port number to listen on (default = random)']
					]

from ConfigParser import Error

def parse_config(data):
	new_config = ConfigParser.SafeConfigParser()
	new_config.readfp(StringIO(data))
	return new_config

def load_config(options):
	with open(options['config-file'], mode='rt') as configfile:
		return parse_config(configfile.read())

