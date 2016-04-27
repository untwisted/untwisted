from untwisted.network import Spin, spawn, xmap, zmap
from traceback import print_exc as debug
from untwisted.event import *
from collections import deque
import socket
import ssl

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
ENOTCONN, ESHUTDOWN, EINTR, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN 

CLOSE_ERR_CODE   = (ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE, EBADF)
ACCEPT_ERR_CODE  = (EWOULDBLOCK, ECONNABORTED, EAGAIN)

class Dump(object):
    def process_error(self, spin, err):
        if err in CLOSE_ERR_CODE: 
            spawn(spin, CLOSE, err)
        else: 
            spawn(spin, SEND_ERR, err)

class DumpStr(Dump):
    __slots__ = 'data'

    def __init__(self, data=''):
        self.data = buffer(data)

    def process(self, spin):
        try:
            size = spin.send(self.data)  
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

    def __nonzero__(self):
        return bool(self.data)

class DumpFile(DumpStr):
    __slots__ = 'fd'
    BLOCK     = 1024 * 124

    def __init__(self, fd):
        self.fd   = fd
        DumpStr.__init__(self)
        self.process_file()

    def process(self, spin):
        DumpStr.process(self, spin)
        if not self.data:
            self.process_file()

    def process_file(self):
        try:
            data = self.fd.read(DumpFile.BLOCK)
        except IOError as excpt:
            spawn(spin, READ_ERR, excpt)
        else:
            self.data = buffer(data)
        
class Stdin:
    """ 
    Stdin is a handle used to send data through Spin connections.

    Methods:
        dump     - Send data through the Spin instance.

        dumpfile - Dump a file through the Spin instance.

    Diagram:
        WRITE -> Stdin -(int:err, int:err, ())-> {**CLOSE, SEND_ERR, DUMPED}
    """

    def __init__(self, spin):
        """ 
        """

        self.queue    = deque()
        self.data     = None
        spin.dump     = self.dump
        spin.dumpfile = self.dumpfile
        self.spin     = spin

    def update(self, spin):
        """
        """
        
        if not self.data: 
            self.process_queue(spin)

        self.data.process(spin)

    def process_queue(self, spin):
        try:
            self.data = self.queue.popleft()
        except IndexError: 
            self.stop()

    def stop(self):
        zmap(self.spin, WRITE, self.update)
        spawn(self.spin, DUMPED)

    def start(self):
        if not self.queue: 
            xmap(self.spin, WRITE, self.update)

    def dump(self, data):
        """ 
        Send data through a Spin instance. 
        """

        self.start()
        dump = DumpStr(data)
        self.queue.append(dump)

    def dumpfile(self, fd):
        """ 
        Dump a file through a Spin instance. 
        """

        self.start()
        dump = DumpFile(fd)
        self.queue.append(dump)

class Stdout(object):
    """
    Used to read data through a Spin instance.

    Diagram:
    
        READ -> Stdout -(int:err, int:err, str:data)-> {**CLOSE, RECV_ERR, LOAD}
    """
    
    SIZE = 1024 * 124

    def __init__(self, spin):
        xmap(spin, READ, self.update)

    def update(self, spin):
        """
        """

        try:
            self.process_data(spin)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])

    def process_data(self, spin):
        data = spin.recv(self.SIZE)

        if not data: 
            spawn(spin, CLOSE, '') 
        else: 
            spawn(spin, LOAD, data)

    def process_error(self, spin, err):
        if err in CLOSE_ERR_CODE: 
            spawn(spin, CLOSE, err)
        else: 
            spawn(spin, RECV_ERR, err)

class Client(object):
    """
    Used to set up TCP clients.

    Diagram:
    
        WRITE -> Client -((), int:err)-> {**CONNECT, **CONNECT_ERR}
    """

    def __init__(self, spin):
        xmap(spin, WRITE, self.update)

    def update(self, spin):
        zmap(spin, WRITE, self.update)
        err = spin.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

        if err != 0:
            spawn(spin, CONNECT_ERR, err)
        else:
            spawn(spin, CONNECT)


class Server(object):
    """
    Used to set up TCP servers.

    READ -> Server -(Spin:client, int:err)-> {ACCEPT, ACCEPT_ERR}
    """

    def __init__(self, spin, wrap = lambda sock: Spin(sock)):
        xmap(spin, READ, self.update)
        self.wrap = wrap

    def update(self, spin):
        while True:
            try:
                sock, addr = spin.accept()
                spawn(spin, ACCEPT, self.wrap(sock))
            except socket.error as excpt:
                err = excpt.args[0]
                if not err in ACCEPT_ERR_CODE:
                    spawn(spin, ACCEPT_ERR, err)
                else:
                    break

def lose(spin):
    """
    It is used to close TCP connection and unregister
    the Spin instance from untwisted reactor.

    Diagram:

        lose -> (int:err | socket.error:err) -> CLOSE_ERR
    """

    try:
        spin.destroy()
    except Exception as err:
        spawn(spin, CLOSE_ERR, err)

    try:
        spin.close()
    except Exception as excpt:
        err = excpt.args[0]
        spawn(spin, CLOSE_ERR, err)

def put(spin, data):
    """
    A handle used to serialize arguments of events.
    
        xmap(con, LOAD, put)
    """
    print data

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
    server.bind(('', 1234))
    server.listen(200)
    Server(server)
    xmap(server, ACCEPT, lambda server, spin: install_basic_handles(spin))
    return server

def install_basic_handles(spin):
    """
    """

    Stdin(spin)
    Stdout(spin)
    xmap(spin, CLOSE, lambda spin, err: lose(spin))

def create_client(addr, port):
    """
    Set up a TCP client and installs the basic handles Stdin, Stdout.

    def send_data(client):
        client.dump('GET / HTTP/1.1\r\n')
        xmap(client, LOAD, iostd.put)

    client = create_client('www.google.com.br', 80)
    xmap(client, CONNECT, send_data)
    """

    spin = Spin()
    Client(spin)
    spin.connect_ex((addr, port))
    xmap(spin, CONNECT, install_basic_handles)
    return spin






