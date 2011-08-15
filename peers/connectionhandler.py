import random
import logging

import args
from baseconnectionhandler import BaseConnectionHandler
from node_id import node_id

log = logging.getLogger('vmesh-peers')

connections = {} # format: {'peer_id': <connection_obj>}
unknown_connections = set() # format: {<connection_obj>}

#
# Handles id tracking and command dispatching
#
class ConnectionHandler(BaseConnectionHandler):
	def __init__(self, socket, server, id=None):
		BaseConnectionHandler.__init__(self, socket)
		self.server = server
		unknown_connections.add(self)
		self.peer_id = id
		if self.peer_id is not None:
			# Outgoing connection
			self.send_msg('my_id_is', node_id)	# push my id to peer

	def handle_close(self):
		unknown_connections.discard(self) # if still unknown, otherwise no-op
		try:
			del connections[self.peer_id]
		except KeyError:
			pass
		BaseConnectionHandler.handle_close(self)

	def keep_me(self):
		# this is idempotent
		connections[self.peer_id] = self
		unknown_connections.discard(self)
		self.send_msg('id_ack')

	def my_id_is(self, payload):
		self.peer_id = payload
		if self.peer_id == node_id:
			log.debug('self-connection detected: dropping')
			self.close_when_done()
		elif self.peer_id in connections:
			"""
			To help resolve race conditions where two nodes try to simutaneously
			connect to each other, we randomly choose a connection to drop.
			Half the time, both nodes will drop the same connection, half the
			time they'll drop different connections (resulting in both being
			dropped and requiring a re-attempt).
			"""
			if random.choice((True, False)):
				# drop this
				log.debug('duplicate connection: dropping unknown connection')
				self.close_when_done()
			else:
				# drop other
				log.debug('duplicate connection: dropping known connection')
				connections[self.peer_id].close_when_done()
				self.keep_me()
		else:
			# regular new node, so stash the connection
			self.keep_me()

	def id_ack(self, _):
		# this is idempotent
		connections[self.peer_id] = self
		unknown_connections.discard(self)

	def dispatch(self, msg):
		try:
			getattr(self, msg.cmd)(msg.payload)
		except AttributeError:
			msg = 'Received invalid command \'%s\' from ' % msg.cmd
			if self.peer_id:
				msg += self.peer.id
			else:
				msg += 'unknown peer'
			log.warning(msg)

