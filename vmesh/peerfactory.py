from twisted.internet import protocol

from peerprotocol import PeerProtocol

class PeerFactory(protocol.Factory):
	protocol = PeerProtocol
	def __init__(self, service):
		self.service = service # stash service

	def startedConnecting(self, connector):
		""" Called when initiating an outgoing connection """
		pass

	def clientConnectionFailed(self, connector, reason):
		""" Called when an attempted outgoing connection failed """
		pass

	def clientConnectionLost(self, connector, reason):
		""" Called when an established outgoing connection was lost """
		pass

