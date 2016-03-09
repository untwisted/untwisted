from untwisted.network import Spin, spawn, xmap, zmap, Erase
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
        self.start()
        dump = DumpStr(data)
        self.queue.append(dump)

    def dumpfile(self, fd):
        self.start()
        dump = DumpFile(fd)
        self.queue.append(dump)

class Stdout(object):
    """
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
    """

    def __init__(self, spin):
        xmap(spin, WRITE, self.update)

    def update(self, spin):
        err = spin.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)

        if err != 0:
            spawn(spin, CONNECT_ERR, err)
        else:
            zmap(spin, WRITE, self.update)
            spawn(spin, CONNECT)

class Server(object):
    """
    """

    def __init__(self, spin):
        xmap(spin, READ, self.update)

    def update(self, spin):
        while True:
            try:
                sock, addr = spin.accept()
                new = spin.__class__(sock)
                spawn(spin, ACCEPT, new)
            except socket.error as excpt:
                err = excpt.args[0]
                if not err in ACCEPT_ERR_CODE:
                    spawn(spin, ACCEPT_ERR, err)
                else:
                    break

def lose(spin):
    spin.destroy()

    try:
        spin.close()
    except Exception as excpt:
        err = excpt.args[0]
        spawn(spin, CLOSE_ERR, err)
        debug()

def put(spin, data):
    print data

def create_server():
    pass

def install_basic_handles(spin):
    """
    """

    Stdin(spin)
    Stdout(spin)
    xmap(spin, CLOSE, lambda spin, err: lose(spin))

def create_client(addr, port):
    """
    """

    spin = Spin()
    Client(spin)
    spin.connect_ex((addr, port))
    xmap(spin, CONNECT, install_basic_handles)
    return spin





