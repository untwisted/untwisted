from untwisted.client import ClientSSL, SSL_CONNECT, SSL_CONNECT_ERR, \
SSL_CERTIFICATE_ERR, put, lose
from untwisted.sock_writer import SockWriterSSL
from untwisted.sock_reader import SockReaderSSL, LOAD, CLOSE
from socket import socket, AF_INET, SOCK_STREAM
from untwisted import core
from untwisted.core import die
from untwisted.network import SuperSocketSSL

import ssl

def handle_close(ssock, err):
    print('Closed.')
    die()

def on_connect(con, host):
    SockWriterSSL(con)
    SockReaderSSL(con)
    con.dump(b"GET / HTTP/1.0\r\nHost: %s\r\n\r\n" % host.encode('utf8'))
    con.add_map(LOAD, put)
    con.add_map(CLOSE, handle_close)

def handle_connect_err(ssock, err):
    print('Connect err.', err)
    die()

def handle_certificate_err(ssock, err):
    print('Certificate err.', err)
    die()

def main(addr, port, host):
    sock    = socket(AF_INET, SOCK_STREAM)
    context = ssl.create_default_context()

    wrap = context.wrap_socket(sock, 
    server_hostname=host, do_handshake_on_connect=False)

    con = SuperSocketSSL(wrap)
    con.connect_ex((addr, port))

    ClientSSL(con)
    con.add_map(SSL_CONNECT, on_connect, host)
    con.add_map(SSL_CONNECT_ERR, handle_connect_err)
    con.add_map(SSL_CERTIFICATE_ERR, handle_certificate_err)

if __name__ == '__main__':
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='localhost')
                  
    parser.add_option("-p", "--port", dest="port",
                      metavar="integer", default=443)

    parser.add_option("-o", "--host", dest="host",
                      metavar="string", default="www.google.com")

    (opt, args) = parser.parse_args()

    main(opt.addr, opt.port, opt.host)
    core.gear.mainloop()
