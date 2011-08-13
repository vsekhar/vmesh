import boto
import args

if args.get('local'):
	metadata = {'public-hostname': 'localhost',
				'ami-launch-index': 0,
				'ami-id': 'ami-localdebug'}
else:
	import boto.utils
	metadata = boto.utils.get_instance_metadata()

def get_sdb_domain(domain=None):
	global args
	if not domain:
		domain = args.get('sdb_domain')
	if args.get('local'):
		sdb = boto.connect_sdb()
	else:
		sdb = boto.connect_sdb(args.get('access_key'), args.get('secret_key'))
	dom = sdb.lookup(domain)
	if dom is None:
		dom = sdb.create_domain(domain)
	return dom

def get_s3_bucket(bucket):
	global args
	if args.get('local'):
		s3conn = boto.connect_s3()
	else:
		s3conn = boto.connect_s3(args.get('access_key'), args.get('secret_key'))
	bucket = s3conn.get_bucket(bucket)
	if bucket is None:
		bucket = s3conn.create_bucket(bucket)
	return bucket

