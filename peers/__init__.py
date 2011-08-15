from twisted.application import service as twisted_service
from twisted.application import internet
from twisted.internet import reactor

import service
import factory

Application = twisted_service.Application # instantiated elsewhere

peerservice = service.PeerService()
factory = factory.PeerFactory(peerservice)
server = reactor.listenTCP(0, factory)
listen_port = server.getHost().port

def connect(host, port):
	reactor.connectTCP(host, port, factory)

