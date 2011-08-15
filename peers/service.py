import random
import string

from twisted.application import service

class PeerService(service.Service):
	def __init__(self):
		# node-wide state goes here
		# TODO: Set this using aws
		self.node_id = ''.join(random.choice(string.digits+string.letters) for _ in xrange(8))
		self.peers = dict()
		self.unknown_peers = set()
		self.config_version = 0
		self.new_config_version = 0

	def kernel_msg(self, msg):
		print msg


