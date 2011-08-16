#!/usr/bin/env python

version = (1,0,0)

import string
import random

from logger import log # do this first to setup logging

import args # processes args
import peers # starts server socket

from taskloop import TaskLoop, Task

def random_string(length = 8):
	return ''.join([random.choice(string.letters + string.digits) for _ in range(length)])

# placeholder kernel processing
def kernel_processing():
	try:
		random_id = random.choice(list(peers.connections.keys()))
		connection = peers.connections[random_id]
	except IndexError:
		pass # no connections
	else:
		msg = random_string()
		connection.send_msg('kernel', msg)	

def peer_processing():
	peers.top_up()
	peers.update_node()
	if args.get('debug'):
		s = 'connections: '
		for c in peers.connections.values():
			s += c.peer_id + ' '
		s += 'unknowns: %d' % len(peers.unknown_connections)
		log.debug(s)

def checkpoint():
	# do checkpoint (stopping the kernel?)
	# tell kernels to checkpoint themselves?
	pass

def check_central_config():
	# if version > args.config_current_version:
	# get newest version, then args.update_config(data, new_version)
	pass

def update_pending_config():
	if args.config_latest_version > args.config_current_version:
		# fetch from SDB/S3
		pass

def cleanup():
	peers.purge_old_peers()

if __name__ == '__main__':
	if args.get('list'):
		for host in peers.hosts():
			print(host.name, host['timestamp'])
		exit(0)

	if args.get('reset'):
		peers.clear_hosts()

	# initialization
	if not args.get('local'):
		import time
		time.sleep(random.randint(0,5)) # spread out initial database hits
	peers.update_node()
	peers.purge_old_peers()

	# main run loop
	tasks = TaskLoop()
	tasks += Task(interval = 0, callback = peers.poll)
	tasks += Task(interval = args.get('kernel_interval'), callback = kernel_processing)
	tasks += Task(interval = args.get('peer_mgmt_interval'), callback = peer_processing)
	tasks += Task(interval = args.get('checkpoint_interval'), callback = checkpoint)
	tasks += Task(interval = args.get('clean_up_interval'), callback = cleanup)
	tasks += Task(interval=5, interval_max=60, callback = check_central_config)
	tasks += Task(interval=0, callback = update_pending_config)

	try:
		tasks.runForever()
	except KeyboardInterrupt:
		print

