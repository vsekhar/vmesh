#!/usr/bin/env python

from baseconnectionhandler import BaseConnectionHandler, poll
import argparse
import socket
import pickle

parser = argparse.ArgumentParser()
parser.add_argument('host', type=str, help='host name or ip')
parser.add_argument('port', type=int, help='port')
args = parser.parse_args()

class ClientConnectionHandler(BaseConnectionHandler):
	def dispatch(self, msg):
		print str(msg)

def main():
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	sock.connect((args.host, args.port))
	client = ClientConnectionHandler(socket=sock) # outgoing connection
	client.send_msg('my_id_is', 'LocalClient')
	while True:
		print '>>> ',
		cmd = raw_input()
		if cmd == 'q' or cmd.startswith('quit'):
			break
		if cmd:
			cmd, _, payload = cmd.partition(' ')
			client.send_msg(cmd=cmd, payload=payload)
		poll()
		

if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print
		pass

