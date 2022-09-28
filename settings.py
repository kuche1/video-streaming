import os

HERE = os.path.dirname(os.path.realpath(__file__))

hostname = ''
port = 8080

use_ssl = False
ssl_keyfile  = os.path.join(HERE, 'certs', 'signed-certs', 'private.key')
ssl_certfile = os.path.join(HERE, 'certs', 'signed-certs', 'certificate.crt')
