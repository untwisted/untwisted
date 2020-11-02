from untwisted.stdin import SockWriter
from untwisted.stdout import SockReader
from untwisted.event import CLOSE, LOAD, DUMPED
from untwisted import dump
import os

class DumpStr(dump.DumpStr):
    def process(self, dev):
        try:
            size = os.write(dev.fd, self.data)  
        except OSError as excpt:
            self.process_error(dev, excpt)
        else:
            self.data = self.data[size:]

class DumpFile(DumpStr, dump.DumpFile):
    pass

class FileWriter(SockWriter):
    """
    Used to dump data through a Device instance.

    """

    def dump(self, data):
        self.start()
        data = DumpStr(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFile(fd)
        self.queue.append(fd)

class FileReader(SockReader):
    """
    Used to read data from a Device instance.

    """

    def update(self, dev):
        try:
            self.process_data(dev)
        except OSError as excpt:
            self.process_error(dev, excpt)

    def process_data(self, dev):
        data = os.read(dev.fd, self.SIZE)
        if not data: 
            dev.drive(CLOSE, '') 
        else: 
            dev.drive(LOAD, data)












