from untwisted.network import core, xmap, READ, WRITE, spawn, zmap
from untwisted import iostd
from untwisted.event import DUMPED, CLOSE, LOAD
from collections import deque

class DumpStr(iostd.DumpStr):
    def process(self, dev):
        try:
            dev.write(self.data)  
        except IOError as excpt:
            spawn(dev, CLOSE, excpt)
        else:
            self.data = buffer('')

class DumpFile(DumpStr, iostd.DumpFile):
    pass

class Stdin(iostd.Stdin):
    def dump(self, data):
        self.start()
        data = DumpStr(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFile(fd)
        self.queue.append(fd)

class Stdout(iostd.Stdout):
    def update(self, dev):
        try:
            self.process_data(dev)
        except IOError as excpt:
            spawn(dev, CLOSE, excpt)

    def process_data(self, dev):
        data = dev.read(self.SIZE)
        spawn(dev, LOAD, data)

def lose(device):
    """
    It is used to close the device and destroy the Device instance.
    """
    device.destroy()
    device.close()







