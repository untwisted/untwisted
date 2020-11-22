from untwisted.event import LOAD, Event
import sys

class Fixed:
    """
    A handle for application layers that demand fixed chunk transmission of data.

    def on_found(spin, data):
        print data

    Fixed(spin, size=4)
    xmap(spin, FOUND, on_found)

    If it arises a chunk of size equal or greater than 4 then FOUND is processed.
    """

    class FOUND(Event):
        pass

    def __init__(self, spin, size=4):
        spin.add_map(LOAD, self.update)
        self.arr  = bytearray()
        self.size = size

    def update(self, spin, data):
        self.arr.extend(data)
        mem  = memoryview(self.arr)
        for ind in range(self.size, len(self.arr) + 1, self.size):
            spin.drive(Fixed.FOUND, mem[ind - self.size:ind].tobytes())
        else:
            del mem
            del self.arr[:ind]
    
class Breaker:
    """
    A handle for application layer protocols which follows a command scheme pattern.

    def on_add(spin, *args):
        print args

    Breaker(spin)
    xmap(spin, 'add', on_add)

    If it arises the sequence of data defined below then on_add is processed and its
    arguments will be ('1', '2', '3').

        'add 1 2 3'

    
    """

    def __init__(self, device, delim=b' '):
        self.delim = delim
        device.add_map(Terminator.FOUND, self.handle_found)

    def handle_found(self, device, data):
        lst = data.split(self.delim)
        device.drive(lst.pop(0), *lst)

class Terminator:
    """
    A handle for application layer protocols that use '\r\n' as token.

    def on_found(spin, data):
        print data

    Terminator(spin, delim='\r\n')
    xmap(spin, FOUND, on_found)

    If it arises the sequence below then on_found is processed.

        'some-data\r\n'
    """

    class FOUND(Event):
        pass

    def __init__(self, spin, delim=b'\r\n'):
        self.delim  = delim
        self.arr    = bytearray()

        spin.add_map(LOAD, self.update)

    def update(self, spin, data):
        # Can be optmized receiving.
        self.arr.extend(data)

        if not self.delim in data:
            return

        data = bytes(self.arr)
        lst  = data.split(self.delim)
        del self.arr[:]
        self.arr.extend(lst.pop(-1))

        for ind in lst:
            spin.drive(Terminator.FOUND, ind)
            
class Accumulator:
    """
    Just an accumulator on LOAD.
    """
    def __init__(self, spin):
        spin.add_map(LOAD, self.update)
        spin.accumulator  = self
        self.data = bytearray()

    def update(self, spin, data):
        self.data.extend(data)

class AccUntil:
    """
    """

    class DONE(Event):
        pass

    def __init__(self, spin, delim=b'\r\n\r\n'):
        self.delim = delim
        self.arr   = bytearray()
        self.spin  = spin

    def start(self, data=b''):
        self.spin.add_map(LOAD, self.update)
        self.update(self.spin, data)

    def update(self, spin, data):
        self.arr.extend(data)
        if self.delim in self.arr:
            self.stop()

    def stop(self):
        self.spin.del_map(LOAD, self.update)
        data = bytes(self.arr)

        a, b = data.split(self.delim, 1)
        self.spin.drive(AccUntil.DONE, a, b)

class TmpFile:
    class DONE(Event):
        pass

    def __init__(self, spin):
        self.spin = spin
        self.fd   = None
        self.size = None

    def start(self, fd, size=0, init_data=b''):
        self.fd = fd
        self.size = size

        self.spin.add_map(LOAD, self.update)
        self.update(self.spin, init_data)

    def stop(self, data):
        lsize = self.size - self.fd.tell()
        self.fd.write(data[:lsize])

        self.spin.del_map(LOAD, self.update)
        self.spin.drive(TmpFile.DONE, self.fd, data[lsize:])

    def update(self, spin, data):
        lsize = self.size - self.fd.tell()
        if len(data) >= lsize: 
            self.stop(data)
        else:
            self.fd.write(data)

def logcon(spin, fd=sys.stdout):
    def log(spin, data):
        fd.write('%s\n' % data)
    spin.add_map(Terminator.FOUND, log)


