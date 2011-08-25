import time
import random
from Queue import Empty

from twisted.internet import reactor, defer
from twisted.python import log

from peerfactory import PeerFactory
from intervalservice import IntervalService

class PeerService(IntervalService, object):
	def __init__(self, superservice):
		super(PeerService, self).__init__(config=superservice.config, section='vmesh')

		# state from superservice
		self.superservice = superservice
		self.options = superservice.options
		self.config_version = superservice.config_version
		self.new_config_version = superservice.new_config_version
		self.config = superservice.config
		self.aws = superservice.aws
		self.outgoing_queue = superservice.outgoing_queue
		self.incoming_queue = superservice.incoming_queue

		# local state
		self.peers = dict()
		self.unknown_peers = set()
		self.listener = None
		self.listen_port = None
		self.factory = PeerFactory(self)

		self.intervalCalls = [self.top_up, self.purge_old_peers, self.update, self.status, self.send]
		for ic in self.intervalCalls:
			self.addInterval(ic)

	def privilegedStartService(self):
		self.listener = reactor.listenTCP(int(self.options['port']), self.factory)
		self.listen_port = self.listener.getHost().port
		return super(PeerService, self).privilegedStartService()

	def startService(self):
		self.node_id = self.superservice.node_id
		return super(PeerService, self).startService()

	def stopService(self):
		ret = list()
		ret.append(defer.maybeDeferred(super(PeerService, self).stopService))
		if self.listener is not None:
			ret.append(defer.maybeDeferred(self.listener.stopListening))
		return defer.DeferredList(ret)

	def connect(self, host, port):
		# print 'Outgoing connection to %s:%d' % (host, port)
		reactor.connectTCP(host, port, self.factory)

	def hosts(self, sort=None):
		query_string = 'SELECT timestamp FROM %s WHERE timestamp is not null ORDER BY timestamp' % self.config.get('vmesh', 'sdb_domain')
		if sort is not None:
			query_string += ' ' + sort
		q = self.aws.query(query_string)
		for host in q:
			yield host

	def clear_hosts(self):
		for host in hosts():
			host.delete()

	def kernel_msg(self, msg):
		log.msg('Kernel msg: %s' % msg)

	###########################################################################
	# Interval calls
	###########################################################################
	def purge_old_peers(self):
		oldest_time = time.time() - float(self.config.get('vmesh', 'peer_entry_lifetime'))
		for host in self.hosts(sort='ASC'):
			if float(host['timestamp']) < oldest_time:
				host.delete()
			else:
				break # hosts are sorted

	def top_up(self):
		deficit = int(self.config.get('vmesh', 'connections')) - len(self.peers)
		if deficit > 0:
			filtered_hosts = filter(lambda x: x.name != self.node_id and x.name not in self.peers, self.hosts(sort='DESC'))
			for host in filtered_hosts:
				h, _, p = host.name.partition(':')
				self.connect(h, int(p))
				deficit -= 1
				if deficit <= 0: break

	def update(self):
		# Have to pad the timestamp to allow for SDB's lexicographic sorting
		# Padding to 12-digits is used, which should give us another 3,000 years...
		# (http://en.wikipedia.org/wiki/Unix_time)

		record = self.aws.getItem(name=self.node_id, create=True)
		record['timestamp'] = '%012d' % time.time()
		record.save()

	def status(self):
		log.msg('Peers: %d; unknowns: %d' % (len(self.peers), len(self.unknown_peers)))

	def send(self):
		if not len(self.peers):
			return
		try:
			while True:
				msg = self.outgoing_queue.get_nowait()
				random_id = random.choice(self.peers.keys())
				connection = self.peers[random_id]
				connection.sendKernelMsg(msg)
		except Empty:
			return


