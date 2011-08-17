#part-handler

import ConfigParser
import cStringIO
import boto

handler_version = 2

def list_types():
	# return a list of mime-types that are handled by this module
	return(["text/vmesh-config"])

def handle_part(data,ctype,filename,payload,frequency=None):
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

	for line in payload.splitlines():
		# get code and install it to /usr/local/lib/python2.7/dist-packages (this is on the default pythonpath)
		print line

	print "==== end ctype=%s filename=%s" % (ctype, filename)

