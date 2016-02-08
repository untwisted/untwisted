"""

"""

from socket import socket
from untwisted.event import READ, WRITE, get_event
from untwisted.mode import *
from untwisted.usual import *
from untwisted import core

class Spin(socket, Mode):
    def __init__(self, sock=None):
        socket.__init__(self, _sock = sock._sock if sock else None)
        Mode.__init__(self)
        self.setblocking(0) 
        core.gear.register(self)

    def bind(self, event, handle, *args):
        Mode.bind(self, event, handle, *args)
        core.gear.scale(self)

    def unbind(self, event, handle, *args):
        Mode.unbind(self, event, handle, *args)
        core.gear.scale(self)

    def destroy(self):
        self.base.clear()
        core.gear.unregister(self)

    def is_writable(self):
        return self.base.get(WRITE)

    def is_readable(self):
        return self.base.get(READ)

class Device(Mode):
    def __init__(self, device):
        from os import O_NONBLOCK
        from fcntl import fcntl, F_GETFL, F_SETFL
        
        Mode.__init__(self)
        self.device = device

        # A non blocking device.
        fd = self.device.fileno()
        fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK)
        core.gear.register(self)

    def bind(self, event, handle, *args):
        Mode.bind(self, event, handle, *args)
        core.gear.scale(self)

    def unbind(self, event, handle, *args):
        Mode.unbind(self, event, handle, *args)
        core.gear.scale(self)

    def destroy(self):
        self.base.clear()
        gear.unregister(self)

    def is_writable(self):
        return self.base.get(WRITE)

    def is_readable(self):
        return self.base.get(READ)

    def __getattr__(self, name):
        return getattr(self.device, name)


# _all__ = ['Spin',  'Device', 'Stop','Root','Kill','spawn','core', 'hold','xmap',
          # 'zmap','READ','WRITE','get_event','install_reactor']






