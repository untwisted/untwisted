from untwisted.wrappers import xmap, zmap, spawn
from untwisted.network import SSL
from untwisted.event import CLOSE, SSL_CERTIFICATE_ERR, \
SSL_CONNECT_ERR, SSL_CONNECT

from untwisted.client_ssl import *
from untwisted.stdin_ssl import *
from untwisted.stdout_ssl import *
from untwisted.iostd import lose
import socket
import ssl

def install_ssl_handles(con):
    StdinSSL(con)
    StdoutSSL(con)
    xmap(con, CLOSE, lambda con, err: lose(con))

def create_client_ssl(addr, port):
    sock    = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    context = ssl.create_default_context()
    con     = SSL(context.wrap_socket(sock, 
    do_handshake_on_connect=False, server_hostname=addr))

    con.connect_ex((addr, port))

    ClientSSL(con)
    xmap(con, SSL_CONNECT, install_ssl_handles)
    xmap(con, SSL_CONNECT_ERR, lambda con, err: lose(err))
    xmap(con, SSL_CERTIFICATE_ERR, lambda con, err: lose(err))
    return con

def create_server_ssl():
    pass







