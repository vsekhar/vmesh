import logging
import sys
import time
import pwd
import os

import args

logging.captureWarnings(True)
logs = list()
logs.append(logging.getLogger('vmesh'))
logs.append(logging.getLogger('vmesh-peers'))

# stream (file) handler
if args.get('local'):
	logfilepath = os.path.join(os.getcwd(), args.get('log')) # use current directory
else:
	userinfo = pwd.getpwuid(os.getuid())
	logfilepath = os.path.join(userinfo.pw_dir, args.get('log')) # user's home dir
logfile = open(logfilepath, 'a')
fh = logging.StreamHandler(stream=logfile) # don't use FileHandler since we have to redirect below
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(levelname)s: %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
fh.setFormatter(formatter)

# console handler
sh = logging.StreamHandler()
sh.setFormatter(formatter)

# add to all loggers
for log in logs:
	log.setLevel(logging.DEBUG if args.get('debug') else logging.INFO)
	log.addHandler(fh)
	log.addHandler(sh)

# default logger
log = logging.getLogger('vmesh')

if not args.get('interactive'):
	# no one is watching, so capture python exception errors and the like
	global old_stdout, old_stderr
	log.info('STDOUT and STDERR redirected to log file: %s' % logfile.name)
	old_stdout = sys.stdout
	old_stderr = sys.stderr
	sys.stdout = logfile
	sys.stderr = logfile

# boto is normally a bit too noisy
logging.getLogger('boto').setLevel(logging.WARNING)

# announce startup
log.info('### Vmesh starting (python %d.%d.%d, timestamp %d) ###' % (sys.version_info[:3] + (time.time(),)))
log.debug('Launched with sys.argv = %s', str(args.safeargv))
log.debug('Working directory: %s' % os.getcwd())
log.info('Logging to: %s' % logfilepath)
if args.get('debug'):
	log.info('Debug logging mode enabled')

