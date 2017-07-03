from untwisted.network import SSL
from untwisted.event import CLOSE, SSL_CERTIFICATE_ERR, \
SSL_CONNECT_ERR, SSL_CONNECT, CONNECT_ERR, LOAD

from untwisted.client_ssl import *
from untwisted.stdin_ssl import *
from untwisted.stdout_ssl import *
from untwisted.iostd import lose
import socket
import ssl

def install_ssl_handles(con):
    StdinSSL(con)
    StdoutSSL(con)
    con.add_map(CLOSE, lambda con, err: lose(con))

def create_client_ssl(addr, port):
    sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    wrap    = context.wrap_socket(sock, 
    do_handshake_on_connect=False, server_hostname=addr)

    # First attempt to connect otherwise it leaves
    # an unconnected spin instance in the reactor.
    wrap.connect_ex((addr, port))
    con = SSL(wrap)

    ClientSSL(con)
    con.add_map(SSL_CONNECT, install_ssl_handles)
    con.add_map(SSL_CONNECT_ERR, lambda con, err: lose(con))
    con.add_map(CONNECT_ERR, lambda con, err: lose(con))
    con.add_map(SSL_CERTIFICATE_ERR, lambda con, err: lose(con))
    return con

def create_server_ssl():
    pass













