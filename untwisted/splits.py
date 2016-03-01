from untwisted.network import core, xmap, READ, WRITE, spawn
from untwisted.event import LOAD, BOX, FOUND
import sys

class Breaker(object):
    def __init__(self, device, delim=' '):
        self.delim = delim
        xmap(device, FOUND, self.handle_found)

    def handle_found(self, device, data):
        tokens = data.split(self.delim, 4)
        event = tokens[0]
        del tokens[0]
        spawn(device, event, *tokens)


class Fixed(object):
    """
    A protocol for fixed chunks.

    It spawns BOX when the accumulator hits the specified
    size in bytes.
    """

    def __init__(self, spin, size=4):
        xmap(spin, LOAD, self.update)

        self.box  = ''
        self.size = size

    def update(self, spin, data):
        self.box = self.box + data

        while len(self.box) >= self.size:
            chunk    = buffer(self.box, 0, 4)
            self.box = buffer(self.box, 4)
            spawn(spin, BOX, chunk)

class Shrug:
    def __init__(self, spin, delim='\r\n'):
        self.delim = delim
        self.msg   = bytearray()

        xmap(spin, LOAD, self.update)

    def update(self, spin, data):
        self.msg.extend(data)

        if not self.delim in data:
            return

        chain = self.msg.split(self.delim)
        self.msg = chain[-1]
        del chain[-1]

        for ind in chain:
            spawn(spin, FOUND, str(ind))
            
class Accumulator(object):
    """
    Just an accumulator on LOAD.
    """
    def __init__(self, spin):
        xmap(spin, LOAD, self.update)
        spin.accumulator  = self
        self.data = ''

    def update(self, spin, data):
        self.data = self.data + data
                
def logcon(spin, fd=sys.stdout):
    def log(spin, data):
        fd.write('%s\n' % data)
    xmap(spin, FOUND, log)








