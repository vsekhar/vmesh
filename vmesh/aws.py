import boto
import boto.utils

class AWS:
	def __init__(self, opt, conf):
		self.local = opt['local']

		# get metadata and create connections
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

		# get/create bucket and domain
		self.s3_bucketname = conf.get('vmesh', 'bucket')
		self.s3_bucket = self.s3.get_bucket(self.s3_bucketname) or self.s3.create_bucket(self.s3_bucketname)
		self.sdb_domainname = conf.get('vmesh', 'sdb_domain')
		self.sdb_domain = self.sdb.lookup(self.sdb_domainname) or self.sdb.create_domain(self.sdb_domainname)

	# --- SDB stuff ----------------------------------------------------------
	def getItem(self, name, create=False):
		item = self.sdb_domain.get_item(name)
		if item is None and create:
			item = self.sdb_domain.new_item(name)
		return item

	def newItem(self, name):
		return self.sdb_domain.new_item(name)

	def query(self, query_string):
		q = self.sdb_domain.select(query_string)
		for item in q: yield item

	# --- S3 stuff -----------------------------------------------------------
	def getKey(self, key_name):
		raise NotImplementedError

