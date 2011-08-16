from twisted.application import service
from twisted.application.internet import TimerService

import aws
from peerservice import PeerService

class NodeService(service.MultiService):
	_base = service.MultiService

	def __init__(self, options):
		self._base.__init__(self)

		self.options = options
		self.config_version = 0
		self.new_config_version = 0

		self.aws = aws.AWS(options)

		self.peerservice = PeerService(options, self)
		# self.timerservice = TimerService(step, func, args, kwargs)
		self.addService(self.peerservice)
		# self.addService(self.timerservice)

		# initialize kernel compute processes

	def startService(self):
		self._base.startService(self)
		self.listen_port = self.peerservice.listen_port
		self.node_id = self.aws.metadata['public-hostname'] + ':' + str(self.listen_port)
		print 'Node ID: %s' % self.node_id

def makeService(options):
	return NodeService(options)

