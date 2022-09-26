#! /usr/bin/env python3

from OpenSSL import crypto, SSL # python3 -m pip install pyopenssl
from socket import gethostname
from pprint import pprint
from time import gmtime, mktime

CERT_FILE = "selfsigned.crt"
KEY_FILE = "private.key"
SIZE = 2048

def create_self_signed_cert():

    # create a key pair
    k = crypto.PKey()
    k.generate_key(crypto.TYPE_RSA, SIZE)

    # create a self-signed cert
    cert = crypto.X509()
    cert.get_subject().C = "UK"
    cert.get_subject().ST = "London"
    cert.get_subject().L = "London"
    cert.get_subject().O = "Dummy Company Ltd 2"
    cert.get_subject().OU = "Dummy Company Ltd 2"
    cert.get_subject().CN = gethostname()
    cert.set_serial_number(1000)
    cert.gmtime_adj_notBefore(0)
    cert.gmtime_adj_notAfter(10*365*24*60*60)
    cert.set_issuer(cert.get_subject())
    cert.set_pubkey(k)
    cert.sign(k, 'sha1')

    
    dumped_cert = crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
    f = open(CERT_FILE, "wb")
    f.write(dumped_cert)
    f.close()
    
    dumped_private = crypto.dump_privatekey(crypto.FILETYPE_PEM, k)
    f= open(KEY_FILE, "wb")
    f.write(dumped_private)
    f.close()

create_self_signed_cert()
