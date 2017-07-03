from socket import socket, AF_INET, SOCK_STREAM
from untwisted.event import READ, WRITE
from untwisted.core import die
from untwisted.dispatcher import *
from untwisted import core
from untwisted.wrappers import *

class SuperSocket(Dispatcher):
    """
    The dispatching system for file descriptors.
    """

    def __init__(self, fd):
        Dispatcher.__init__(self)
        self.fd = fd
        core.gear.register(self)
        self.dead = False

    def destroy(self):
        core.gear.unregister(self)
        self.dead = True

class Spin(SuperSocket):
    """
    The dispatching system for sockets.
    """

    def __init__(self, sock=None):
        self.sock = sock if sock else socket()
        SuperSocket.__init__(self, self.sock.fileno())
        self.sock.setblocking(0) 
        self.con_err = None

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def connect_as(self, *args):
        """
        This method warrants no exception is going to be thrown
        even with gaierrors. it sets self.con_err
        to the exception it was raised.
        """

        try:
            self.sock.connect_ex(*args)
        except Exception as e:
            self.con_err = e

class Device(SuperSocket):
    """
    The dispatching system for child processes.
    """

    def __init__(self, device):
        from os import O_NONBLOCK
        from fcntl import fcntl, F_GETFL, F_SETFL
        
        self.device = device
        SuperSocket.__init__(self, self.device.fileno())

        # A non blocking device.
        fcntl(self.fd, F_SETFL, fcntl(self.fd, F_GETFL) | O_NONBLOCK)

    def __getattr__(self, name):
        return getattr(self.device, name)

class SSL(Spin):
    """
    Dispatching system for SSL sockets.
    """

    pass



