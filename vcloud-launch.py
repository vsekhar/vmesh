#!/usr/bin/env python

version = (1,0,0)

import time
import string
import random

import args # processes args
import peers # starts server socket

from logger import log

def random_string(length = 8):
	return ''.join([random.choice(string.letters + string.digits) for _ in range(length)])

if __name__ == '__main__':
	if args.get('list'):
		for host in peers.hosts():
			print(host.name, host['timestamp'])
		exit(0)

	# space out remote instances so they don't all hit the DB at the same time
	if not args.get('local'):
		import time
		time.sleep(random.randint(0,5))

	if args.get('reset'):
		peers.clear_hosts()

	# management intervals
	config_check_time = time.time()
	peer_mgmt_time = time.time()
	kernel_time = time.time()
	checkpoint_time = time.time()
	clean_up_time = time.time()

	# initialization
	peers.update_node()
	peers.purge_old_peers()

	# main run loop
	try:
		while(1):
			peers.poll()

			cur_time = time.time()

			# randomly check for updated configuration every 5-60 seconds and
			# broadcast if found
			if cur_time - config_check_time > random.randint(5,60):
				pass
				# if version > args.config_current_version:
				# get newest version, then args.update_config(data, new_version)


			# update configuration if one is pending
			if args.config_latest_version > args.config_current_version:
				# fetch from SDB/S3
				pass


			# kernel processing
			if cur_time - kernel_time > args.get('kernel_interval'):
				try:
					random_id = random.choice(list(peers.connections.keys()))
					connection = peers.connections[random_id]
				except IndexError:
					pass
				else:
					msg = random_string()
					connection.send_msg('kernel', msg)
				finally:
					kernel_time = cur_time

			# peer processing
			if cur_time - peer_mgmt_time > args.get('peer_mgmt_interval'):
				peer_mgmt_time = cur_time
				peers.top_up()
				peers.update_node()
				if args.get('debug'):
					s = 'connections: '
					for c in peers.connections.values():
						s += c.peer_id + ' '
					s += 'unknowns: %d' % len(peers.unknown_connections)
					log.debug(s)

			# checkpoint
			if cur_time - checkpoint_time > args.get('checkpoint_interval'):
				# do checkpoint (stopping the kernel?)
				# tell kernels to checkpoint themselves?
				pass

			# clean-up
			if cur_time - clean_up_time > args.get('clean_up_interval'):
				peers.purge_old_peers()
	except KeyboardInterrupt:
		pass

