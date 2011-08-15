import peers

application = peers.Application('vmesh')

# test with a self connection
peers.connect('localhost', peers.listen_port)

