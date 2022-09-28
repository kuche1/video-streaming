import os

HERE = os.path.dirname(os.path.realpath(__file__))

hostname = ''
port = 8080

use_threading = True

run_http_on_ports = [8880]
run_https_on_ports = [4443]
ssl_keyfile  = os.path.join(HERE, 'certs', 'signed-certs', 'private.key')
ssl_certfile = os.path.join(HERE, 'certs', 'signed-certs', 'certificate.crt')
