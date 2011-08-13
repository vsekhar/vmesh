import asyncore
import socket
import random

from logger import log
from baseconnectionhandler import BaseConnectionHandler, poll
import args
import aws

connections = {} # format: {'peer_id': <connection_obj>}
unknown_connections = set() # format: {<connection_obj>}

#
# Handles id tracking, command dispatching and authentication
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

	###################################################
	# Protocol commands
	###################################################

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

	def hello(self, _):
		self.send_msg('hello-to-you')

	def kernel(self, payload):
		log.debug('kernel message received: %s' % payload)

	def new_config(self, new_version):
		if args.new_config_available(new_version):
			broadcast_new_config(new_version)

	def config_version(self, _):
		self.send_msg('my_config_version', args.config_current_version)

	###################################################
	# Command registration and dispatching
	###################################################
	command_table = {
		'my_id_is': my_id_is,
		'id_ack': id_ack,
		'hello': hello,
		'kernel': kernel,
		'new_config': new_config,
		'config_version': config_version
	}

	def dispatch(self, msg):
		# run code depending on msg type, payload, etc.
		try:
			self.command_table[msg.cmd](self, msg.payload)
		except KeyError:
			msg = 'Received invalid command \'%s\' from ' % msg.cmd
			if self.peer_id:
				msg += self.peer.id
			else:
				msg += 'unknown peer'
			log.warning(msg)

class ServerSocket(asyncore.dispatcher):
    def __init__(self, bind_address='', port=0):
        asyncore.dispatcher.__init__(self)
        self.create_socket(asyncore.socket.AF_INET,
                           asyncore.socket.SOCK_STREAM)
        self.bind((bind_address, port))
        self.port = int(self.socket.getsockname()[1])
        self.listen(1)

    def handle_accept(self):
        sock, address = self.accept()
        log.debug('incoming connection from %s' % str(address))
        ConnectionHandler(socket=sock, server=self, id=None) # incoming connection

    def handle_close(self):
        self.close()

serversocket = ServerSocket()
hostname = aws.metadata['public-hostname']
node_id = hostname + ':' + str(serversocket.port)
log.info('Node ID: %s' % node_id)
sdb_domain = aws.get_sdb_domain()

def new_connection(id):
	addr,_,port = id.partition(':')
	port = int(port)
	sock = socket.create_connection((addr,port))
	log.debug('outgoing connection to %s' % id)
	ConnectionHandler(socket=sock, server=serversocket, id=id) # outgoing connection

def hosts(ascending=False):
	query_string = 'SELECT timestamp FROM %s WHERE timestamp is not null ORDER BY timestamp ' % args.get('sdb_domain')
	query_string += 'ASC' if ascending else 'DESC'
	q = sdb_domain.select(query_string)
	for host in q:
		yield host

def clear_hosts():
	for host in hosts():
		host.delete()

def top_up():
	deficit = int(args.get('connections')) - len(connections)
	if deficit > 0:
		count = 0
		for host in hosts():
			if count >= deficit:
				return # done
			if host.name == node_id:
				continue # skip self
			if host.name in connections:
				continue # skip dupes
			try:
				new_connection(host.name)
				count += 1
			except socket.error:
				pass

def print_peers():
	import time
	print('Peers (hostname, port, age):')
	cur_time = time.time()
	for host in hosts():
		print(host.name, cur_time - float(host['timestamp']))

def purge_old_peers(lifetime=int(args.get('peer_entry_lifetime'))):
	import time
	cur_time = time.time()
	oldest_time = cur_time - lifetime
	for host in hosts(ascending=True):
		if float(host['timestamp']) < oldest_time:
			host.delete()
		else:
			break # hosts are sorted oldest-first

def update_node():
	record = sdb_domain.get_item(node_id)
	if record is None:
		record = sdb_domain.new_item(node_id)
	import time
	cur_time = time.time()
	record['timestamp'] = cur_time
	record.save()

def broadcast_new_config(new_version):
	for conn in connections.values():
		conn.send_msg(cmd='new_config', payload=new_version)


