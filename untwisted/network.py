from socket import socket
from untwisted.event import READ, WRITE, EXPT, ERROR, DESTROY
from untwisted.dispatcher import *
from untwisted.core import die
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
        self.drive(DESTROY)

class SSL(SuperSocket):
    """
    Dispatching system for SSL sockets.
    """
    def __init__(self, sock):
        self.sock = sock
        SuperSocket.__init__(self, sock.fileno())
        self.sock.setblocking(0) 

    def __getattr__(self, name):
        return getattr(self.sock, name)

class Spin(socket, SuperSocket):
    """
    The dispatching system for sockets.
    """

    def __init__(self, sock=None):
        socket.__init__(self, _sock = sock._sock if sock else None)
        self.setblocking(0) 
        SuperSocket.__init__(self, self.fileno())

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









