import args

include_flag = '### VMESH-INCLUDE'

def load_with_includes(filename, passthrough):
	ret = ''
	with open(filename, mode='rt') as cfile:
		for line in cfile:
			if line.startswith(include_flag):
				for var in passthrough:
					ret += '%s = %s\n' % (var, args.get(var))
			else:
				ret += line
	return ret


