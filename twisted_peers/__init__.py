from twisted.application import service as twisted_service
from twisted.internet import reactor

import service
import factory

application = twisted_service.Application('vmesh')
peerservice = service.PeerService()
factory = factory.PeerFactory(peerservice)
server = reactor.listenTCP(0, factory)
listen_port = server.getHost().port

def connect(host, port):
	internet.TCPClient(host, port, factory).setServiceParent(servicecollection)

