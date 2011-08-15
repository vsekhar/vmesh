import args
import logging
from connectionhandler import ConnectionHandler, connections, unknown_connections

log = logging.getLogger('vmesh_peers')

class PeerHandler(ConnectionHandler):
	def __init__(self, socket, server, id=None):
		ConnectionHandler.__init__(self, socket, server, id)

	def hello(self, _):
		self.send_msg('hello-to-you')

	def kernel(self, payload):
		log.debug('kernel message received: %s' % payload)

	def new_config(self, new_version):
		if args.new_config_available(new_version):
			broadcast_new_config(new_version)

	def config_version(self, _):
		self.send_msg('my_config_version', args.config_current_version)

