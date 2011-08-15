from twisted.internet import protocol

from protocol import PeerProtocol

class PeerFactory(protocol.Factory):
	protocol = PeerProtocol
	def __init__(self, service): self.service = service # stash service

