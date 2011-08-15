import asyncore
import logging

import aws

log = logging.getLogger('vmesh-peers')

class ServerSocket(asyncore.dispatcher):
    def __init__(self, bind_address='', port=0):
        asyncore.dispatcher.__init__(self)
        self.create_socket(asyncore.socket.AF_INET,
                           asyncore.socket.SOCK_STREAM)
        self.bind((bind_address, port))
        self.port = int(self.socket.getsockname()[1])
        self.listen(1)

    def handle_accept(self):
		from peerhandler import PeerHandler # must be deferred because peerhandler needs node_id
		sock, address = self.accept()
		log.debug('incoming connection from %s' % str(address))
		PeerHandler(socket=sock, server=self, id=None) # incoming connection

    def handle_close(self):
        self.close()

poll = asyncore.poll
serversocket = ServerSocket()

