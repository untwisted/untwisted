"""

"""

from socket import socket
from untwisted.event import READ, WRITE, EXPT, ERROR
from untwisted.dispatcher import *
from untwisted.core import die
from untwisted import core

class SSL(Dispatcher):
    def __init__(self, sock):
        Dispatcher.__init__(self)
        self.sock = sock
        self.fd = self.sock.fileno()
        core.gear.register(self)

    def add_map(self, event, handle, *args):
        Dispatcher.add_map(self, event, handle, *args)
        core.gear.scale(self)

    def del_map(self, event, handle, *args):
        Dispatcher.del_map(self, event, handle, *args)
        core.gear.scale(self)

    def __getattr__(self, name):
        return getattr(self.sock, name)

    def destroy(self):
        self.base.clear()
        SSL.base.clear()
        del self.pool[:]
        core.gear.unregister(self)

class Spin(socket, Dispatcher):
    def __init__(self, sock=None):
        socket.__init__(self, _sock = sock._sock if sock else None)
        Dispatcher.__init__(self)
        self.setblocking(0) 
        self.fd = self.fileno()
        core.gear.register(self)

    def add_map(self, event, handle, *args):
        Dispatcher.add_map(self, event, handle, *args)
        core.gear.scale(self)

    def del_map(self, event, handle, *args):
        Dispatcher.del_map(self, event, handle, *args)
        core.gear.scale(self)

    def destroy(self):
        self.base.clear()
        Spin.base.clear()
        del self.pool[:]
        core.gear.unregister(self)

class Device(Dispatcher):
    def __init__(self, device):
        from os import O_NONBLOCK
        from fcntl import fcntl, F_GETFL, F_SETFL
        
        Dispatcher.__init__(self)
        self.device = device

        # A non blocking device.
        self.fd = self.device.fileno()
        fcntl(self.fd, F_SETFL, fcntl(self.fd, F_GETFL) | O_NONBLOCK)
        core.gear.register(self)

    def add_map(self, event, handle, *args):
        Dispatcher.add_map(self, event, handle, *args)
        core.gear.scale(self)

    def del_map(self, event, handle, *args):
        Dispatcher.del_map(self, event, handle, *args)
        core.gear.scale(self)

    def destroy(self):
        self.base.clear()
        Device.base.clear()
        del self.pool[:]
        gear.unregister(self)

    def __getattr__(self, name):
        return getattr(self.device, name)


# _all__ = ['Spin',  'Device', 'Stop','Root','Kill','spawn','core', 'hold','xmap',
          # 'zmap','READ','WRITE','get_event','install_reactor']







