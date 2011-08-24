from twisted.protocols import amp

import kernelcommands

class KernelProtocol(amp.AMP, object):
	def __init__(self):
		ret = super(PeerProtocol, self).connectionMade()

		# function forwarding (to make this behave like a ProcessProtocol)
		self.outReceived = self.dataReceived
		self.processEnded = self.connectionLost

		self.data = ''
		self.sequence = None

		return ret

	@kernelcommands.Hello.responder
	def hello():
		return {'hello_response': 'well hello to you'}

	@kernelcommands.Echo.responder
	def echo(echo_msg):
		return {'echo_response': echo_msg}

	@ kernelcommands.Data.responder
	def data(data, sequence, more):
		if self.sequence is None or sequence == self.sequence + 1:
			self.data += data
			self.sequence += 1
		else:
			raise RuntimeError('KernelProtocol: Non-sequential sequence number')

		if not more:
			print 'Data received %s' % self.data
			data = ''
			self.sequence = None

