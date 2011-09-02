#!/usr/bin/python

import shlex
import sys
import os
import tempfile
import subprocess

import boto

import launch
import setup

def launch_local(config):
	with tempfile.NamedTemporaryFile(mode='w+t') as configfile:
		configfile.write(config)
		configfile.flush()
		configfile.seek(0)
		command = 'twistd -n vmesh --local'
		if launch.get_arg('debug'):
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
	import StringIO, gzip
	from contextlib import closing

	if launch.get_arg('spot_instances'):
		requests = launch.ec2.request_spot_instances(
								price=launch.get_arg('price'),
								image_id=launch.get_arg('ami'),
								count=launch.get_arg('count'),
								instance_type=launch.get_arg('instance_type'),
								type=('persistent' if launch.get_arg('persistent') else 'one-time'),
								key_name=launch.get_arg('key_pair'),
								security_groups=launch.get_arg('security_groups'),
								user_data=user_data
								)
		return requests
	else:
		reservation = launch.ec2.run_instances(
								image_id=launch.get_arg('ami'),
								min_count=launch.get_arg('count'),
								max_count=launch.get_arg('count'),
								key_name=launch.get_arg('key_pair'),
								security_groups=launch.get_arg('security_groups'),
								instance_type=launch.get_arg('instance_type'),
								user_data=user_data
								)
		return reservation

def launch_bare():
	return launch.ec2.run_instances(
				image_id=launch.get_arg('ami'),
				min_count=launch.get_arg('count'),
				max_count=launch.get_arg('count'),
				key_name=launch.get_arg('key_pair'),
				security_groups=launch.get_arg('security_groups'),
				instance_type=launch.get_arg('instance_type')
				)


if __name__ == '__main__':
	if launch.get_arg('bare'):
		print launch_bare()
		sys.exit(0)

	bucketname = launch.get_arg('bucket')
	# packagename = launch.get_arg('package_name')
	eggfilename = launch.get_arg('egg_file_name')

	# slipstream credentials into config file
	from launch.include import load_with_includes
	passthrough = ['node_access_key', 'node_secret_key', 'bucket', 'egg_file_name', 'package_name']
	config = load_with_includes('vmesh-config.txt', passthrough=passthrough)
	if launch.get_arg('config_only'):
		print config
		sys.exit(0)

	if launch.get_arg('local'):
		ret = launch_local(config)
		sys.exit(ret)

	# build the egg
	old_argv = sys.argv # trick setup into thinking it was executed at the command line
	sys.argv = ['setup.py', '-q', 'bdist_egg']
	dist = setup.run()
	egg_path = os.path.join('dist', dist.get_fullname())
	egg_path += '-py%d.%d.egg' % (sys.version_info[0], sys.version_info[1])

	# upload the egg
	b = launch.s3.get_bucket(bucketname)
	if not b:
		b = s3.create_bucket(bucketname)
	k = b.get_key(eggfilename)
	if not k:
		k = b.new_key(eggfilename)

	print 'Uploading %s as s3:%s/%s' % (egg_path, bucketname, eggfilename)
	def report_progress(at, total):
		print '\r%d%%' % ((at/total)*100),
		sys.stdout.flush()
	k.set_contents_from_file(open(egg_path, mode='rb'), cb=report_progress)
	print ' done'

	if launch.get_arg('upload_only'):
		sys.exit(0)

	# create multipart userdata
	with tempfile.NamedTemporaryFile() as configfile:
		configfile.write(config)
		configfile.seek(0)
		command = 'write-mime-multipart -z'
		command += ' cloud-config'
		command += ' vmesh-job'
		command += ' parthandler.py'
		command += ' %s:text/vmesh-config' % configfile.name
		p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE)
		out, err = p.communicate()
		if p.returncode != 0 or err is not None:
			print >> sys.stderr, err
			print out
			print >> sys.stderr, 'write-mime-multipart return code: %d' % p.returncode

	print launch_remote(out)

