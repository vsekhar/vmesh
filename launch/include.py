import args

def load_with_includes(filename, passthrough):
	ret = ''
	with open(filename, mode='rt') as cfile:
		for line in cfile:
			if line.startswith('### VMESH-INCLUDE'):
				# special launcher-provided variables
				for var in passthrough:
					ret += '%s = %s\n' % (var, args.get(var))
			else:
				ret += line
	return ret


