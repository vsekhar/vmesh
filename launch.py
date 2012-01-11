#!/usr/bin/python

import shlex
import sys
import os
import tempfile
import subprocess
from contextlib import closing

import local
import setup

def launch_local(config):
	with tempfile.NamedTemporaryFile(mode='w+t') as configfile:
		configfile.write(config)
		configfile.flush()
		configfile.seek(0)
		command = 'twistd -n  --prefix vmesh vmesh --local'
		if local.get_arg('debug'):
			command += ' --debug'
		command += ' --config-file ' + configfile.name
		print 'Launching with command: %s' % command
		try:
			p = subprocess.Popen(shlex.split(command))
			p.wait()
		except KeyboardInterrupt:
			pass
		finally:
			return p.returncode

def launch_remote(user_data):
	if local.get_arg('spot_instances'):
		requests = local.ec2.request_spot_instances(
								price=local.get_arg('price'),
								image_id=local.get_arg('ami'),
								count=local.get_arg('count'),
								instance_type=local.get_arg('instance_type'),
								type=('persistent' if local.get_arg('persistent') else 'one-time'),
								key_name=local.get_arg('key_pair'),
								security_groups=local.get_arg('security_groups'),
								user_data=user_data
								)
		return requests
	else:
		reservation = local.ec2.run_instances(
								image_id=local.get_arg('ami'),
								min_count=local.get_arg('count'),
								max_count=local.get_arg('count'),
								key_name=local.get_arg('key_pair'),
								security_groups=local.get_arg('security_groups'),
								instance_type=local.get_arg('instance_type'),
								user_data=user_data
								)
		return reservation

def launch_bare():
	return local.ec2.run_instances(
				image_id=local.get_arg('ami'),
				min_count=local.get_arg('count'),
				max_count=local.get_arg('count'),
				key_name=local.get_arg('key_pair'),
				security_groups=local.get_arg('security_groups'),
				instance_type=local.get_arg('instance_type')
				)


if __name__ == '__main__':
	if local.get_arg('bare'):
		print launch_bare()
		sys.exit(0)

	bucketname = local.get_arg('bucket')
	# packagename = local.get_arg('package_name')
	eggfilename = local.get_arg('egg_file_name')

	# slipstream credentials into config file
	from local.include import load_with_includes
	passthrough = ['node_access_key', 'node_secret_key', 'bucket', 'egg_file_name', 'package_name']
	config = load_with_includes('vmesh-config.txt', passthrough=passthrough)
	if local.get_arg('config_only'):
		print config
		sys.exit(0)

	if local.get_arg('local'):
		ret = launch_local(config)
		sys.exit(ret)

	# build the egg
	old_argv = sys.argv # trick setup into thinking it was executed at the command line
	sys.argv = ['setup.py', '-q', 'bdist_egg']
	dist = setup.run()
	egg_path = os.path.join('dist', dist.get_fullname())
	egg_path += '-py%d.%d.egg' % (sys.version_info[0], sys.version_info[1])

	# upload the egg
	b = local.s3.get_bucket(bucketname)
	if not b:
		b = local.s3.create_bucket(bucketname)
	k = b.get_key(eggfilename)
	if not k:
		k = b.new_key(eggfilename)

	print 'Uploading %s as s3:%s/%s' % (egg_path, bucketname, eggfilename)
	def report_progress(at, total):
		print '\r%d%%' % ((at/total)*100),
		sys.stdout.flush()
	with closing(open(egg_path, mode='rb')) as egg:
		k.set_contents_from_file(egg, cb=report_progress)
	print ' done'

	if local.get_arg('upload_only'):
		sys.exit(0)

	# create multipart userdata
	with tempfile.NamedTemporaryFile() as configfile:
		configfile.write(config)
		configfile.flush()
		configfile.seek(0)
		command = 'write-mime-multipart -z'
		command += ' cloud-config'
		command += ' vmesh-job'
		command += ' parthandler.py'
		command += ' %s:text/vmesh-config' % configfile.name
		p = subprocess.Popen(shlex.split(command), stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = p.communicate()
		if p.returncode != 0 or err != '':
			print >> sys.stderr, err
			print out
			print >> sys.stderr, 'write-mime-multipart return code: %d' % p.returncode
			sys.exit(1)

	print launch_remote(out)

