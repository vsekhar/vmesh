from twisted.protocols import amp

class Hello(amp.Command):
	""" Basic ping """
	response = [('hello_response', amp.String())]

class Echo(amp.Command):
	""" Basic echo of a string """
	arguments = [('echo_msg', amp.String())]
	response = [('echo_response', amp.String())]

class Data(amp.Command):
	""" Send a chunk of data """
	arguments = [('data', amp.String()),
				('sequence', amp.Integer()),
				('more', amp.Boolean())]
	errors = {RuntimeError: 'RuntimeError'}

