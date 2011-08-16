from twisted.application import service
from twisted.internet import reactor

from factory import PeerFactory

class PeerService(service.Service):
	_base = service.Service

	def __init__(self, options, superservice):
		#service.Service.__init__(self)
		# node-wide state goes here
		# TODO: Set this using aws
		self.superservice = superservice
		self.peers = dict()
		self.unknown_peers = set()
		self.options = options
		self.listener = None
		self.listen_port = None
		self.factory = PeerFactory(self)

	def startService(self):
		self._base.startService(self)
		if self.listener is None:
			self.listener = reactor.listenTCP(int(self.options['port']), self.factory)
		self.listen_port = self.listener.getHost().port

	def stopService(self):
		self._base.stopService(self)
		if self.listener is not None:
			d = self.listener.stopListening()
			return d

	def connect(host, port):
		reactor.connectTCP(host, port, self.factory)

	def kernel_msg(self, msg):
		print msg

