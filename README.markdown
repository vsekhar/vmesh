VMesh
=====

Simple distributed computing

## Pre-requisites

Ubuntu packages:

	sudo apt-get install python-setuptools python-twisted python-boto python-zope.interface euca2ools

Configuration and environment:

* Copy `dot-vmesh.template` to `$HOME/.vmesh` and fill in access credentials

Run locally (in debug mode): `./launch.py -ldc <config_name>`

Run remotely: `./launch.py -c <config_name> [-n <num_instances>]`

