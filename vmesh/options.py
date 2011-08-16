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

	optParameters = [['access-key', None, None, 'AWS access key to use']
					,['secret-key', None, None, 'AWS secret key to use']
					,['config', 'c', None, 'Config file to use (default=./config)']
					,['log', None, None, 'Logfile to use (default=twisted-defined)']
					,['port', 'p', 0, 'The port number to listen on (default = random)']
					]

from ConfigParser import Error

def parse_config(data):
	new_config = ConfigParser.SafeConfigParser()
	new_config.readfp(StringIO(data))
	return new_config

def load_config(options):
	if options.has_key('config') and options['config'] is not None:
		filename = options['config']
	else:
		filename = 'config'
	return parse_config(''.join(open(filename, 'rt').readlines()))

