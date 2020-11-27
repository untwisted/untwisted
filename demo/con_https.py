from untwisted.client import ClientSSL, SSL_CONNECT, SSL_CONNECT_ERR, \
SSL_CERTIFICATE_ERR, put, lose
from untwisted.sock_writer import SockWriterSSL
from untwisted.sock_reader import SockReaderSSL, LOAD, CLOSE
from socket import socket, AF_INET, SOCK_STREAM
from untwisted import core
from untwisted.core import die
from untwisted.network import SSL

import ssl

def on_connect(con, host):
    SockWriterSSL(con)
    SockReaderSSL(con)
    con.dump(b"GET / HTTP/1.0\r\nHost: %s\r\n\r\n" % host.encode('utf8'))
    con.add_map(LOAD, put)
    con.add_map(CLOSE, lambda con, err: lose(con))
    con.add_map(CLOSE, lambda con, err: die())

def main(addr, port, host):
    sock    = socket(AF_INET, SOCK_STREAM)
    context = ssl.create_default_context()
    con     = SSL(context.wrap_socket(sock, do_handshake_on_connect=False, server_hostname=host))
    con.connect_ex((addr, port))

    ClientSSL(con)
    con.add_map(SSL_CONNECT, on_connect, host)
    con.add_map(SSL_CONNECT_ERR, lambda con, err: die(err))
    con.add_map(SSL_CERTIFICATE_ERR, lambda con, err: die(err))

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









