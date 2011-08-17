import boto
import boto.utils

class AWS:
	def __init__(self, opt, conf):
		self.local = opt['local']
		if self.local:
			self.metadata = {'public-hostname': 'localhost',
						'ami-launch-index': 0,
						'ami-id': 'ami-localdebug'}
			self.sdb = boto.connect_sdb()
			self.s3 = boto.connect_s3()
		elif conf.has_option('vmesh', 'node_access_key') and conf.has_option('vmesh', 'node_secret_key'):
			self.metadata = boto.utils.get_instance_metadata()
			self.sdb = boto.connect_sdb(conf.get('vmesh', 'node_access_key'), conf.get('vmesh', 'node_secret_key'))
			self.s3 = boto.connect_s3(conf.get('vmesh', 'node_access_key'), conf.get('vmesh', 'node_secret_key'))
		else:
			raise RuntimeError('Need access_key and secret_key for non-local execution')

	def createDomain(self, domain):
		return self.sdb.create_domain(domain)

	def getDomain(self, domain, create=False):
		dom = self.sdb.lookup(domain)
		if dom is None and create:
			print 'Creating domain %s' % domain
			dom = self.createDomain(domain)
		return dom

	def createBucket(self, bucket):
		return self.s3.create_bucket(bucket)

	def getBucket(self, bucket, create=False):
		bucket = self.s3.get_bucket(bucket)
		if bucket is None and create:
			bucket = self.createBucket(bucket)
		return bucket

