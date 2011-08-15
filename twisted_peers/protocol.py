import random

from twisted.protocols import amp
from twisted.internet import defer

import commands

class PeerProtocol(amp.AMP):

	def connectionMade(self):
		amp.AMP.connectionMade(self)

		# 'global' state shortcut
		self.svc = self.factory.service

		# request id if incoming
		d = self.callRemote(commands.GetId
					).addCallback(self.setRemoteId
					).setErrback(lambda r: self.transport.loseConnection())
		defer.Deferred(d)

	def connectionLost(self):
		self.svc.unknown_peers.discard(self) # idempotent
		try:
			del self.svc.peers[self.remote_id]
		except KeyError: pass
		amp.AMP.connectionLost(self)

	def keepMe(self, remote_id):
		self.svc.unknown_peers.discard(self)
		self.svc.peers[remote_id] = self

	def setRemoteId(self, result):
		remote_id = result['my_id']
		if remote_id == self.svc.node_id:
			self.transport.loseConnection() # drop self-connections
		elif remote_id in self.svc.peers:
			"""
			To resolve race conditions where two nodes try to simutaneously
			connect to each other, we randomly choose a connection to drop.
			Half the time, both nodes will drop the same connection, half the
			time they'll drop different connections (resulting in both being
			dropped and requiring a re-attempt).
			"""
			if random.choice((True, False)):
				self.transport.loseConnection() # drop this one
				# log.debug('duplicate connection: dropping new connection')
			else:
				connections[self.peer_id].transport.loseConnection() # drop other one
				self.keep_me(remote_id)
				# log.debug('duplicate connection: dropping previous connection')
		else:
			# no self-connection or dupes, so stash
			self.keep_me(remote_id)

	@commands.Hello.responder
	def hello(self):
		return {'hello_response': 'well hello there'}

	@commands.Echo.responder
	def echo(self, echo_msg):
		return {'echo_response': msg}

	@commands.GetId.responder
	def getid(self):
		return {'my_id': self.svc.node_id}

	@commands.GetConfigVersion.responder
	def getconfigversion(self):
		return {'my_config_version': self.svc.config_version}

	@commands.NewConfigVersion.responder
	def newconfigversion(self, new_version):
		self.svc.new_config_version = max(newversion, self.svc.new_config_version)

	@commands.KernelMsg.responder
	def kernelmsg(self, kernel_msg):
		print self.svc.kernel_msg(kernel_msg)

