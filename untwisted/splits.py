from untwisted.network import core, xmap, zmap, READ, WRITE, spawn
from untwisted.event import LOAD, get_event

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
    """
    FOUND = get_event()
    def __init__(self, spin, size=4):
        xmap(spin, LOAD, self.update)

        self.box  = ''
        self.size = size

    def update(self, spin, data):
        self.box = self.box + data

        while len(self.box) >= self.size:
            chunk    = buffer(self.box, 0, 4)
            self.box = buffer(self.box, 4)
            spawn(spin, Fixed.FOUND, chunk)

class Terminator:
    FOUND = get_event()
    def __init__(self, spin, delim='\r\n'):
        self.delim  = delim
        self.arr    = bytearray()

        xmap(spin, LOAD, self.update)

    def update(self, spin, data):
        self.arr.extend(data)

        if not self.delim in data:
            return

        data = str(self.arr)
        lst  = data.split(self.delim)
        del self.arr[:]
        self.arr.extend(lst.pop(-1))

        for ind in lst:
            spawn(spin, Terminator.FOUND, ind)
            
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

class AccUntil(object):
    DONE = get_event()
    def __init__(self, spin, data='', delim='\r\n\r\n'):
        self.delim = delim
        self.arr   = bytearray()
        self.spin  = spin
        xmap(spin, LOAD, self.update)
        self.update(spin, data)

    def update(self, spin, data):
        self.arr.extend(data)
        if self.delim in self.arr:
            self.process(spin)

    def process(self, spin):
        zmap(spin, LOAD, self.update)
        a, b = self.arr.split(self.delim, 1)
        spawn(spin, AccUntil.DONE, str(a), str(b))

class TmpFile(object):
    DONE = get_event()

    def __init__(self, spin, data, max_size, fd):
        self.fd       = fd
        self.max_size = max_size
        xmap(spin, LOAD, self.update)

        self.update(spin, data)

    def update(self, spin, data):
        pos   = self.fd.tell()
        count = self.max_size - pos
        self.fd.write(data[:count])

        if len(data) < count: 
            return

        zmap(spin, LOAD, self.update)
        spawn(spin, TmpFile.DONE, self.fd, data[count:])

# class AccAck(object):
    # DONE = get_event()
# 
    # def __init__(self, spin, fd, max_size, ack):
        # self.fd       = fd
        # self.max_size = size
        # xmap(spin, LOAD, self.update)
# 
    # def update(self, spin, data):
        # self.fd.write(data)
        # spin.dump(self.ack(fd, self.max_size))
# 
        # if self.fd.tell() >= self.max_size:
            # pass

def logcon(spin, fd=sys.stdout):
    def log(spin, data):
        fd.write('%s\n' % data)
    xmap(spin, Terminator.FOUND, log)







