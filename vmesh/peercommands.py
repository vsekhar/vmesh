from twisted.protocols import amp

class Hello(amp.Command):
	""" Basic ping """
	response = [('hello_response', amp.String())]

class Echo(amp.Command):
	""" Basic echo of a string """
	arguments = [('echo_msg', amp.String())]
	response = [('echo_response', amp.String())]

class GetId(amp.Command):
	""" Command sent by node requesting other node's ID """
	response = [('my_id', amp.String())]

class GetConfigVersion(amp.Command):
	""" Request remote node's config version """
	response = [('my_config_version', amp.Integer())]

class NewConfigVersion(amp.Command):
	""" Indicate a (possibly) newer version of the config is available """
	arguments = [('new_version', amp.Integer())]

class KernelMsg(amp.Command):
	""" Send a kernel message """
	arguments = [('kernel_msg', amp.Unicode())]
	response = [('ok', amp.Boolean())]

class FlowControl(amp.Command):
	""" Set flow control for sender """
	arguments = [('kernel', amp.Boolean())]

