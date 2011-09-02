import boto
import args

try:
	ec2 = boto.connect_ec2(aws_access_key=args.get('local_access_key', section='local'),
							aws_secret_access_key=args.get('local_secret_key', section='local'))
except args.NoOptionError, args.NoSectionError:
	ec2 = boto.connect_ec2()

try:
	s3 = boto.connect_s3(aws_access_key=args.get('local_access_key', section='local'),
							aws_secret_access_key=args.get('local_secret_key', section='local'))
except args.NoOptionError, args.NoSectionError:
	s3 = boto.connect_s3()

