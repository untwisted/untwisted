from untwisted.network import Spin, spawn, xmap, zmap, Erase
from untwisted.event import *
from untwisted.usual import debug
from collections import deque
import socket
import ssl
import sys

from errno import EALREADY, EINPROGRESS, EWOULDBLOCK, ECONNRESET, EINVAL, \
ENOTCONN, ESHUTDOWN, EINTR, EISCONN, EBADF, ECONNABORTED, EPIPE, EAGAIN 

CLOSE_ERR_CODE   = (ECONNRESET, ENOTCONN, ESHUTDOWN, ECONNABORTED, EPIPE, EBADF)
ACCEPT_ERR_CODE  = (EWOULDBLOCK, ECONNABORTED, EAGAIN)

class Stdin:
    """ 
    """

    def __init__(self, spin):
        """ 
        """

        self.queue = deque()
        self.spin  = spin 
        self.data  = ''
        spin.dump  = self.dump

    def update(self, spin):
        """
        """

        if not self.data: 
            self.process_queue(spin)

        try:
            size = spin.send(self.data)  
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

    def process_queue(self, spin):
        try:
            self.data = self.queue.popleft()
        except IndexError: 
            zmap(spin, WRITE, self.update)
            spawn(spin, DUMPED)

    def process_error(self, spin, err):
        if err in CLOSE_ERR_CODE: 
            spawn(spin, CLOSE, err)
        else: 
            spawn(spin, SEND_ERR, err)

    def dump(self, data):
        if not self.queue: 
            xmap(self.spin, WRITE, self.update)
        self.queue.append(buffer(data))

class Stdout(object):
    """
    """
    
    # The max amount of data that is read.
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
                new = Spin(sock)
                spawn(spin, ACCEPT, new)
            except socket.error as excpt:
                err = excpt.args[0]
                if not err in ACCEPT_ERR_CODE:
                    spawn(spin, ACCEPT_ERR, err)
                else:
                    break

class DumpFile(object):
    """
    """

    def __init__(self, spin, fd):
        self.fd    = fd
        self.data  = ''
        
        self.BLOCK = 1024 * 124

        xmap(spin, WRITE, self.update)

    def update(self, spin):
        try:
            if not self.data:
                self.data = self.fd.read(self.BLOCK)
                if not self.data:
                    zmap(spin, WRITE, self.update)
                    spawn(spin, DUMPED_FILE)
                    return

            size      = spin.send(self.data)
            self.data = buffer(self.data, size)
        except socket.error as excpt:
            err = excpt.args[0]
            if err in CLOSE_ERR_CODE:
                spawn(spin, CLOSE)
            else:
                spawn(spin, SEND_ERR, excpt)
        except IOError as excpt:
            err = excpt.args[0]
            spawn(spin, READ_ERR, err)

def lose(spin):
    spin.destroy()

    try:
        spin.close()
    except Exception as excpt:
        err = excpt.args[0]
        spawn(spin, CLOSE_ERR, err)
        debug()

put = lambda spin, data: sys.stdout.write(data)

def create_server():
    pass

def create_client():
    pass



