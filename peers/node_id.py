import logging

import serversocket
import aws

log = logging.getLogger('vmesh-peers')
hostname = aws.metadata['public-hostname']
node_id = hostname + ':' + str(serversocket.serversocket.port)
log.info('Node ID: %s' % node_id)

