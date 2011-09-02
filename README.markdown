VMesh

Simple distributed computing

## Pre-requisites

Ubuntu packages:

	sudo apt-get install python-setuptools python-twisted python-boto python-zope.interface euca2ools

Configuration and environment:
 * Add bin directory to your path for easy acccess to launch/connect/terminate code
 * Copy `dot-vmesh.template` to `$HOME/.vmesh` and fill in access credentials

Run locally:
 * Setup python to find the package using `sudo ./setup.py develop`
 * Create local config file using `launch.py -c <config_name> --config-only > config`
 * Run with `twistd -n vmesh -ldc config`

