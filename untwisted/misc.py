from untwisted.mode import Mode
from untwisted.network import core
from os import O_NONBLOCK
from fcntl import fcntl, F_GETFL, F_SETFL

class Device(Mode):
    def __init__(self, device):
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




