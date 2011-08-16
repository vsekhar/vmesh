import multiprocessing
from Queue import Empty
import random
import string

from twisted.application.internet import TimerService
from twisted.internet import defer

from intervalservice import IntervalService

def random_string(length=8):
	return ''.join([random.choice(string.digits + string.letters) for _ in xrange(length)])

class KernelService(IntervalService, object):
	def __init__(self, superservice):
		super(KernelService, self).__init__(config=superservice.config, section='kernel')
		self.superservice = superservice
		self.options = superservice.options
		self.config = superservice.config

		self.addInterval(self.mgmt)

		self.incoming_queue = multiprocessing.Queue()
		self.outgoing_queue = multiprocessing.Queue()

	def mgmt(self):
		# shuttle messages to/from kernels
		# print 'Kernel mgmt running'
		try:
			while True:
				print 'Kernel msg: %s' % self.incoming_queue.get_nowait()
		except Empty:
			pass
		self.outgoing_queue.put(random_string())

