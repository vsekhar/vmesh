import time
import random

class Task:
	def __init__(self, interval, callback, interval_max=None, name=None, last_time=None, args=None, kwargs=None):
		self._interval = interval
		self._interval_max = interval_max
		self._cur_interval = random.uniform(self._interval, self._interval_max or self._interval)
		self._cb = callback
		self._last = last_time or time.time()
		self._args = args or ()
		self._kwargs = kwargs or {}
		self._name = name

	def __call__(self, *args, **kwargs):
		if self._interval > 10:
			print 'Running %s' % self._cb.__name__
		self._last = time.time()
		return self._cb(*(args or self._args), **(kwargs or self._kwargs))

	def ready(self, cur_time):
		if self._last + self._cur_interval <= cur_time:
			if self._interval_max is not None:
				self._cur_interval = random.uniform(self._interval, self._interval_max)
			return True
		else:
			return False

	def __str__(self):
		return 'IntervalCall \'%s\' (every %f, last %f)' % (self._name, self._interval, self._last)

class TaskLoop:
	def __init__(self):
		self._tasks = []

	def __add__(self, task):
		self._tasks.append(task)
		return self

	def setTasks(self, tasks):
		self._tasks = tasks

	def runOnce(self):
		cur_time = time.time()
		return [task() for task in self._tasks if task.ready(cur_time)]

	def runForever(self, granularity=0.0):
		""" Run loop forever, with each iteration taking at least 'granularity' seconds """
		while(True):
			start_time = time.time()
			self.runOnce()
			delta = time.time() - start_time
			if delta < granularity:
				time.sleep(granularity - delta)

