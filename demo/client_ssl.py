from untwisted.network import core, SSL, xmap, die
from untwisted.iostd import put, lose
from untwisted.iossl import Client, Stdin, Stdout, SSL_CONNECT, SSL_CONNECT_ERR, SSL_CERTIFICATE_ERR, CLOSE, LOAD
from socket import socket, AF_INET, SOCK_STREAM
import ssl

def on_connect(con, host):
    Stdin(con)
    Stdout(con)
    con.dump("GET / HTTP/1.0\r\nHost: %s\r\n\r\n" % host)
    xmap(con, LOAD, put)
    xmap(con, CLOSE, lambda con, err: lose(con))

def main(addr, port, host):
    sock    = socket(AF_INET, SOCK_STREAM)
    context = ssl.create_default_context()
    con     = SSL(context.wrap_socket(sock, do_handshake_on_connect=False, server_hostname=host))
    con.connect_ex((addr, port))

    Client(con)
    xmap(con, SSL_CONNECT, on_connect, host)
    xmap(con, SSL_CONNECT_ERR, lambda con, err: die(err))
    xmap(con, SSL_CERTIFICATE_ERR, lambda con, err: die(err))

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







