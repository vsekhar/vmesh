import datetime
import pickle
from asynchat import async_chat
from asyncore import poll

class Message:
	def __init__(self, cmd, payload=None):
		self.cmd = cmd
		self.payload = payload

	def __str__(self):
		return 'Message(%s, %s)' % (self.cmd, self.payload)

#
# Handles basic message communication, and timestamping
# Requires sub-class to overload dispatch() for actual processing
#
class BaseConnectionHandler(async_chat):

	COMMAND_TERMINATOR = b'\n'

	def __init__(self, socket):
		async_chat.__init__(self, sock=socket)
		self.set_terminator(self.COMMAND_TERMINATOR)
		self.ibuffer=[]
		self.update_timestamp()

	def collect_incoming_data(self, data):
		self.ibuffer.append(data)

	def found_terminator(self):
		data = b''.join(self.ibuffer)
		self.ibuffer = []
		if isinstance(self.get_terminator(), int):
			# process binary, reset for ascii length parameter
			self.dispatch(pickle.loads(data)) # defined in derived class
			self.set_terminator(self.COMMAND_TERMINATOR)

		else:
			# start collecting binary
			length = int(data.decode('ascii').strip())
			self.set_terminator(length)

	def handle_write(self):
		async_chat.handle_write(self)
		self.update_timestamp()

	def handle_read(self):
		async_chat.handle_read(self)
		self.update_timestamp()

	def update_timestamp(self):
		self.timestamp = datetime.datetime.utcnow()

	def send_msg(self, cmd, payload=None):
		data = pickle.dumps(Message(cmd=cmd, payload=payload))
		msg_hdr = str(len(data))
		msg_hdr = msg_hdr.encode('ascii') + self.COMMAND_TERMINATOR
		self.push(msg_hdr + data)

