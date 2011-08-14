import serversocket
import aws
from logger import log

hostname = aws.metadata['public-hostname']
node_id = hostname + ':' + str(serversocket.serversocket.port)
log.info('Node ID: %s' % node_id)

