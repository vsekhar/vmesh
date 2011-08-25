from twisted.application import service
from twisted.python import log

import aws
import options
from peerservice import PeerService
from kernelservice import KernelService

class NodeService(service.MultiService, object):
	def __init__(self, opt):
		super(NodeService, self).__init__()

		# local state
		self.options = opt
		self.config_version = 0
		self.new_config_version = 0
		self.config = options.load_config(self.options)
		self.aws = aws.AWS(self.options, self.config)

		# services
		self.kernelservice = KernelService(self)
		self.addService(self.kernelservice)

		self.incoming_queue = self.kernelservice.incoming_queue
		self.outgoing_queue = self.kernelservice.outgoing_queue

		self.peerservice = PeerService(self)
		self.addService(self.peerservice)

	def startService(self):
		self.listen_port = self.peerservice.listen_port # port was opened in privilegedStartService()
		self.node_id = self.aws.metadata['public-hostname'] + ':' + str(self.listen_port)
		log.msg('Node ID: %s' % self.node_id)
		return super(NodeService, self).startService() # starts all added services

# Entry point via the tap
def makeService(options):
	return NodeService(options)

