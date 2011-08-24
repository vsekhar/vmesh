import random

from twisted.protocols import amp
from twisted.internet import defer

import peercommands

class PeerProtocol(amp.AMP, object):

	def connectionMade(self):
		ret = super(PeerProtocol, self).connectionMade()

		# 'global' state shortcut
		self.svc = self.factory.service

		# request id if incoming
		self.remote_id = None
		self.getRemoteId()

		return ret

	def connectionLost(self, reason):
		self.svc.unknown_peers.discard(self) # idempotent
		try:
			if self.remote_id:
				del self.svc.peers[self.remote_id]
		except KeyError: pass
		return super(PeerProtocol, self).connectionLost(reason)

	def keepMe(self, remote_id):
		print 'Keeping connection to %s' % remote_id
		self.remote_id = remote_id
		self.svc.unknown_peers.discard(self)
		self.svc.peers[remote_id] = self

	def ErrBack(self, reason):
		""" Generic errback that just logs error and drops the connection """
		hostinfo = self.transport.getHost()
		host = hostinfo.host
		port = hostinfo.port
		print 'Error on connection (%s:%s): %s' % (host, port, reason.value)
		self.transport.loseConnection()

	def getRemoteId(self):
		d = self.callRemote(peercommands.GetId)
		d.addCallback(self.setRemoteId)
		d.addErrback(self.ErrBack)
		defer.Deferred(d)

	def sendKernelMsg(self, msg):
		d = self.callRemote(peercommands.KernelMsg, kernel_msg=msg)
		d.addCallback(lambda r: self.getRemoteId() if not r['ok'] else None)
		d.addErrback(self.ErrBack)
		defer.Deferred(d)

	def setRemoteId(self, result):
		remote_id = result['my_id']
		print 'Got ID: %s' % remote_id
		if remote_id == self.svc.node_id:
			print 'self-connection to %s: dropping' % remote_id
			self.transport.loseConnection() # drop self-connections
		elif remote_id in self.svc.peers:
			"""
			To resolve race conditions where two nodes try to simutaneously
			connect to each other, we randomly choose a connection to drop.
			Half the time, both nodes will drop the same connection, half the
			time they'll drop different connections (resulting in both being
			dropped and requiring a re-attempt).
			"""
			print 'Duplicate connection %s' % remote_id			
			if random.choice((True, False)):
				self.transport.loseConnection() # drop this one
				print 'duplicate connection: dropping new connection'
			else:
				connections[self.peer_id].transport.loseConnection() # drop other one
				self.keep_me(remote_id)
				print 'duplicate connection: dropping previous connection'
		else:
			# no self-connection or dupes, so stash
			self.keepMe(remote_id)

	@peercommands.Hello.responder
	def hello(self):
		return {'hello_response': 'well hello there'}

	@peercommands.Echo.responder
	def echo(self, echo_msg):
		return {'echo_response': msg}

	@peercommands.GetId.responder
	def getid(self):
		return {'my_id': self.svc.node_id}

	@peercommands.GetConfigVersion.responder
	def getconfigversion(self):
		return {'my_config_version': self.svc.config_version}

	@peercommands.NewConfigVersion.responder
	def newconfigversion(self, new_version):
		self.svc.new_config_version = max(newversion, self.svc.new_config_version)
		return {}

	@peercommands.KernelMsg.responder
	def kernelmsg(self, kernel_msg):
		if self.remote_id:
			self.svc.incoming_queue.put(kernel_msg)
			return {'ok': True}
		else:
			return {'ok': False}

