import multiprocessing
from Queue import Empty
import random
import string

from twisted.application.internet import TimerService
from twisted.internet import defer

from intervalservice import IntervalService
from kernelprotocol import KernelProtocol

"""
	TODO: a single large container for orgs, and multiple processes for running
	them (with locked access to the full population via python functions).

	If 
"""

def random_string(length=8):
	return ''.join([random.choice(string.digits + string.letters) for _ in xrange(length)])

def random_mgmt(inqueue, outqueue):
	# shuttle messages to/from kernels
	try:
		while True:
			print 'Kernel msg: %s' % inqueue.get_nowait()
	except Empty: pass
	outqueue.put(random_string())


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
		pass

