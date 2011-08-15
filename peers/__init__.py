import socket
import random
import logging

from peerhandler import PeerHandler, connections, unknown_connections
from serversocket import serversocket, poll
from node_id import node_id
import args
import aws

log = logging.getLogger('vmesh-peers')
sdb_domain = aws.get_sdb_domain()

def new_connection(id):
	addr,_,port = id.partition(':')
	port = int(port)
	sock = socket.create_connection((addr,port))
	log.debug('outgoing connection to %s' % id)
	PeerHandler(socket=sock, server=serversocket, id=id) # outgoing connection

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


