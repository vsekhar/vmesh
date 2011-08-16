import boto
import boto.utils

class AWS:
	def __init__(self, options):
		self.local = options['local']
		if self.local:
			self.metadata = {'public-hostname': 'localhost',
						'ami-launch-index': 0,
						'ami-id': 'ami-localdebug'}
			self.sdb = boto.connect_sdb()
			self.s3 = boto.connect_s3()
		elif options.has_key('access_key') and options.has_key('secret_key'):
			self.metadata = boto.utils.get_instance_metadata()
			self.sdb = boto.connect_sdb(access_key, secret_key)
			self.s3 = boto.connect_s3(access_key, secret_key)
		else:
			raise RuntimeError('Need access_key and secret_key for non-local execution')

	def createDomain(domain):
		return self.sdb.create_domain(domain)

	def getDomain(domain, create=False):
		dom = self.sdb.lookup(domain)
		if dom is None and create:
			dom = self.createDomain(domain)
		return dom

	def createBucket(bucket):
		return self.s3.create_bucket(bucket)

	def getBucket(bucket, create=False):
		bucket = self.s3.get_bucket(bucket)
		if bucket is None and create:
			bucket = self.createBucket(bucket)
		return bucket

