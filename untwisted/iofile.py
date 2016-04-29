from untwisted.network import xmap, spawn
from untwisted import iostd
from untwisted.event import CLOSE, LOAD, DUMPED
import os

class DumpStr(iostd.DumpStr):
    def process(self, dev):
        try:
            size = os.write(dev.fd, self.data)  
        except OSError as excpt:
            self.process_error(dev, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

class DumpFile(DumpStr, iostd.DumpFile):
    pass

class Stdin(iostd.Stdin):
    """
    Used to dump data through a Device instance.

    Methods:
        dump     - Send data through a Device instance.

        dumpfile - Dump a file through a Device instance.

    Diagram:
        WRITE -> Stdin -(int:err, ())-> {**CLOSE, DUMPED}

    """

    def dump(self, data):
        self.start()
        data = DumpStr(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFile(fd)
        self.queue.append(fd)

class Stdout(iostd.Stdout):
    """
    Used to read data from a Device instance.

    Diagram:
    
        READ -> Stdout -(int:err, int:err, str:data)-> {**CLOSE, RECV_ERR, LOAD}
    """

    def update(self, dev):
        try:
            self.process_data(dev)
        except OSError as excpt:
            self.process_error(dev, excpt.args[0])

    def process_data(self, dev):
        data = os.read(dev.fd, self.SIZE)
        if not data: 
            spawn(dev, CLOSE, '') 
        else: 
            spawn(dev, LOAD, data)

def lose(device):
    """
    It is used to close the device and destroy the Device instance.
    """
    device.destroy()
    device.close()






