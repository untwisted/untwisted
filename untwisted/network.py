from untwisted.dispatcher import Dispatcher
from socket import socket
from untwisted import core

class BaseSocket(Dispatcher):
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

class SuperSocket(BaseSocket):
    """
    The dispatching system for sockets.
    """

    def __init__(self, sock=None):
        self.sock = sock if sock else socket()
        BaseSocket.__init__(self, self.sock.fileno())
        self.sock.setblocking(0) 

    def __getattr__(self, name):
        return getattr(self.sock, name)

class Device(SuperSocket):
    """
    The dispatching system for child processes.
    """

    def __init__(self, device):
        from os import O_NONBLOCK
        from fcntl import fcntl, F_GETFL, F_SETFL
        
        self.device = device
        BaseSocket.__init__(self, self.device.fileno())

        # A non blocking device.
        fcntl(self.fd, F_SETFL, fcntl(self.fd, F_GETFL) | O_NONBLOCK)

    def __getattr__(self, name):
        return getattr(self.device, name)

class SSL(SuperSocket):
    """
    Dispatching system for SSL sockets.
    """

    pass

class Extension:
    def __init__(self, sock):
        self.sock = sock



