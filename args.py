#!/usr/bin/env python

import argparse
import ConfigParser
import sys
import os
import ast

# create safe argv (for logging, etc.)
def hider(x):
	if x.startswith('--access-key') or x.startswith('--secret-key'):
		return x.partition('=')[0] + '=[hidden]'
	else:
		return x
safeargv = list(map(hider, sys.argv))

# parse command line
parser = argparse.ArgumentParser(description='vmesh-launch.py: initial package script')
parser.add_argument('-c', '--config-file', type=str, help='config file (default=\'config\')')
parser.add_argument('-l', '--local', default=False, action='store_true', help='run in local/debug mode (no AWS metadata, implies --interactive)')
parser.add_argument('--log', type=str, default='vmesh.log', help='log file')
parser.add_argument('-i', '--interactive', default=False, action='store_true', help='interactive (don\' redirect console to logfile)')
parser.add_argument('-d', '--debug', default=False, action='store_true', help='debug (print more output)')
parser.add_argument('--list', default=False, action='store_true', help='list hosts and exit (do not register this host)')
parser.add_argument('-r', '--reset', default=False, action='store_true', help='reset metadata at startup')
parser.add_argument('--access-key', type=str, help='access key')
parser.add_argument('--secret-key', type=str, help='secret key')
parsed_args = parser.parse_args()

if parsed_args.local:
	parsed_args.interactive = True

if not parsed_args.config_file:
	if __name__ == '__main__':
		parsed_args.config_file = os.path.join(os.getcwd(), 'config')
	else:
		parsed_args.config_file = os.path.join(os.path.dirname(__file__), 'config')

config = ConfigParser.SafeConfigParser()
config.read(parsed_args.config_file)

# combined getter
def get(name, section=None):
	global parsed_args, config
	try:
		return getattr(parsed_args, name) # command-line overrides configuration file
	except AttributeError:
		return ast.literal_eval(config.get(section or 'DEFAULT', name))

