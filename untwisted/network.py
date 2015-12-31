""" The untwisted core. """


from untwisted.usual import *
from untwisted.magic import *
from socket import *
from untwisted.core import *
from untwisted.core import Dead
from untwisted import core


class Spin(Dead):
    def __init__(self, sock=None):
        Dead.__init__(self, sock)
        core.gear.register(self)

class Device(Mode):
    def __init__(self, device):
        from os import O_NONBLOCK
        from fcntl import fcntl, F_GETFL, F_SETFL
        
        Mode.__init__(self)
        self.device = device

        # I must make it a non blocking device.

        fd = self.device.fileno()
        fcntl(fd, F_SETFL, fcntl(fd, F_GETFL) | O_NONBLOCK)

        # It registers itself in the reactor.        
        core.gear.register(self)

    def destroy(self):
        core.gear.unregister(self)
        self.base.clear()

    def __getattr__(self, name):
        return getattr(self.device, name)




_all__ = [
            'Spin', 
            'Device', 
            'Stop',
            'Root',
            'Kill',
            'spawn',
            'core', 
            'hold',
            'xmap',
            'rmap',
            'imap',
            'cmap',
            'nmap',
            'mmap',
            'smap',
            'hook',
            'READ',
            'WRITE',
            'get_event',
            'zmap',
            'install_reactor'
          ]








