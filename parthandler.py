#part-handler

import os
import stat
import sys
import ConfigParser
import cStringIO
from contextlib import closing

import boto

handler_version = 2

def list_types():
	# return a list of mime-types that are handled by this module
	return(["text/vmesh-config"])

def handle_part(data,ctype,filename,payload,frequency=None, local=False):
	# data: the cloudinit object
	# ctype: '__begin__', '__end__', or the specific mime-type of the part
	# filename: the filename for the part, or dynamically generated part if
	#           no filename is given attribute is present
	# payload: the content of the part (empty for begin or end)
	# frequency: the frequency that this cloud-init run is running for
	#            this is either 'per-instance' or 'always'.  'per-instance'
	#            will be invoked only on the first boot.  'always' will
	#            will be called on subsequent boots.
	if ctype == "__begin__":
		return
	if ctype == "__end__":
		return

	print "==== received ctype=%s filename=%s ====" % (ctype,filename)

	# load config which gives us credentials and locations to get package
	sio = cStringIO.StringIO(payload)
	config = ConfigParser.SafeConfigParser()
	config.readfp(sio, filename)
	sio.close()

	# get code egg and install it using easy_install
	s3 = boto.connect_s3(config.get('DEFAULT', 'node_access_key'), config.get('DEFAULT', 'node_secret_key'))
	bucket_name = config.get('DEFAULT', 'bucket')
	egg_file_name = config.get('DEFAULT', 'egg_file_name')
	package_name = config.get('DEFAULT', 'package_name')

	bucket = s3.get_bucket(bucket_name)
	if not bucket:
		print 'Bucket does not exist: %s' % bucket_name
		sys.exit(1)
	key = bucket.get_key(egg_file_name)
	if not key:
		print 'Bucket \'%s\' does not have key \'%s\'' % (bucket_name, egg_file_name)

	# save the egg and config
	path = './varlibvmesh' if local else '/var/lib/vmesh'
	try: os.mkdir(path)
	except OSError: pass
	with closing(open(os.path.join(path, egg_file_name), 'wb')) as eggfile:
		key.get_contents_to_file(eggfile)
	print 'Wrote s3:%s/%s to %s' % (bucket_name, egg_file_name, eggfile.name)
	with closing(open(os.path.join(path, 'config'), 'wt')) as configfile:
		os.fchmod(configfile.fileno(), stat.S_IREAD | stat.S_IWRITE)
		configfile.write(payload)
	print 'Wrote vmesh-config to %s' % configfile.name

	print "==== end ctype=%s filename=%s" % (ctype, filename)

if __name__ == '__main__':
	import sys
	handle_part(None, None, None, open(sys.argv[1]).read(), None, local=True)

