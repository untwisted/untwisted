from untwisted.event import LOAD, Event
import sys

class Fixed:
    """
    """

    class FOUND(Event):
        pass

    def __init__(self, ssock, size=4):
        ssock.add_map(LOAD, self.update)
        self.arr  = bytearray()
        self.size = size

    def update(self, ssock, data):
        self.arr.extend(data)
        mem  = memoryview(self.arr)
        for ind in range(self.size, len(self.arr) + 1, self.size):
            ssock.drive(Fixed.FOUND, mem[ind - self.size:ind].tobytes())
        else:
            del mem
            del self.arr[:ind]
    
class Breaker:
    """
    """

    def __init__(self, device, delim=b' '):
        self.delim = delim
        device.add_map(Terminator.FOUND, self.handle_found)

    def handle_found(self, device, data):
        lst = data.split(self.delim)
        device.drive(lst.pop(0), *lst)

class Terminator:
    """
    """

    class FOUND(Event):
        pass

    def __init__(self, ssock, delim=b'\r\n'):
        self.delim  = delim
        self.arr = bytearray()

        ssock.add_map(LOAD, self.update)
        self.ssock = ssock

    def update(self, ssock, data):
        self.arr.extend(data)
        chunks = self.arr.split(self.delim)
        if chunks:
            self.raise_events(chunks)

    def raise_events(self, chunks):
        self.arr.extend(chunks.pop(-1))
        for ind in chunks:
            self.ssock.drive(Terminator.FOUND, bytes(ind))
        self.arr.clear()
            
class Accumulator:
    """
    Just an accumulator on LOAD.
    """
    def __init__(self, ssock):
        ssock.add_map(LOAD, self.update)
        ssock.accumulator  = self
        self.data = bytearray()

    def update(self, ssock, data):
        self.data.extend(data)

class AccUntil:
    """
    """

    class DONE(Event):
        pass

    def __init__(self, ssock, delim=b'\r\n\r\n'):
        self.delim = delim
        self.arr   = bytearray()
        self.ssock  = ssock

    def start(self, data=b''):
        self.ssock.add_map(LOAD, self.update)
        self.update(self.ssock, data)

    def update(self, ssock, data):
        self.arr.extend(data)
        if self.delim in self.arr:
            self.stop()

    def stop(self):
        self.ssock.del_map(LOAD, self.update)
        data = bytes(self.arr)

        a, b = data.split(self.delim, 1)
        self.ssock.drive(AccUntil.DONE, a, b)

class TmpFile:
    class DONE(Event):
        pass

    def __init__(self, ssock):
        self.ssock = ssock
        self.fd   = None
        self.size = None

    def start(self, fd, size=0, init_data=b''):
        self.fd = fd
        self.size = size

        self.ssock.add_map(LOAD, self.update)
        self.update(self.ssock, init_data)

    def stop(self, data):
        lsize = self.size - self.fd.tell()
        self.fd.write(data[:lsize])

        self.ssock.del_map(LOAD, self.update)
        self.ssock.drive(TmpFile.DONE, self.fd, data[lsize:])

    def update(self, ssock, data):
        lsize = self.size - self.fd.tell()
        if len(data) >= lsize: 
            self.stop(data)
        else:
            self.fd.write(data)

def logcon(ssock, fd=sys.stdout):
    def log(ssock, data):
        fd.write('%s\n' % data)
    ssock.add_map(Terminator.FOUND, log)


