from twisted.application.internet import TimerService
from twisted.application import service

class IntervalService(service.MultiService, object):
	""" A MultiService that can easily add interval calls, using intervals from
		a provided config """

	def __init__(self, config, section):
		super(IntervalService, self).__init__()
		self.config = config
		self.section = section
		self.intervalTimers = dict()

	def addInterval(self, func, section=None):
		if section is None: section = self.section
		interval = float(self.config.get(section, func.__name__+'_interval'))
		if interval >= 0: # negative intervals disable the function
			timer = TimerService(interval, func)
			self.intervalTimers[func.__name__] = timer
			self.addService(timer)

