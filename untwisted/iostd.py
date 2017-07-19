from __future__ import print_function
from untwisted.network import Spin

from untwisted.client import *
from untwisted.stdin import *
from untwisted.stdout import *
from untwisted.server import *
from untwisted.event import CLOSE_ERR, LOST

def lose(spin):
    """
    It is used to close TCP connection and unregister
    the Spin instance from untwisted reactor.

    Diagram:

    lose -> (int:err | socket.error:err) -> CLOSE_ERR
    """

    try:
        spin.close()
    except Exception as excpt:
        err = excpt.args[0]
        spin.drive(CLOSE_ERR, err)
    finally:
        spin.destroy()
        spin.drive(LOST)

def put(spin, data):
    """
    A handle used to serialize arguments of events.
    
    xmap(con, LOAD, put)
    """
    print(data)

def create_server(addr, port, backlog):
    """
    Set up a TCP server and installs the basic handles Stdin, Stdout in the
    clients.

    Example:    

    def send_data(server, client):
        # No need to install Stdin or Stdout.
        client.dump('foo bar!')

    server = create_server('0.0.0.0', 1024, 50)
    xmap(server, on_accept, send_data)
    """

    server = Spin()
    server.bind((addr, port))
    server.listen(backlog)
    Server(server)
    server.add_map(ACCEPT, lambda server, spin: install_basic_handles(spin))
    return server

def install_basic_handles(spin):
    """
    """

    Stdin(spin)
    Stdout(spin)
    spin.add_map(CLOSE, lambda spin, err: lose(spin))

def create_client(addr, port):
    """
    Set up a TCP client and installs the basic handles Stdin, Stdout.

    def send_data(client):
        client.dump('GET / HTTP/1.1\r\n')
        xmap(client, LOAD, iostd.put)

    client = create_client('www.google.com.br', 80)
    xmap(client, CONNECT, send_data)
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # First attempt to connect otherwise it leaves
    # an unconnected spin instance in the reactor.
    sock.connect_ex((addr, port))

    spin = Spin(sock)
    Client(spin)
    spin.add_map(CONNECT, install_basic_handles)
    spin.add_map(CONNECT_ERR, lambda con, err: lose(con))
    return spin









