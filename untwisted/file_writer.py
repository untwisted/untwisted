from untwisted.sock_writer import SockWriter
from untwisted.event import CLOSE, LOAD, DUMPED
from untwisted import sock_writer
import os

class DumpStr(sock_writer.DumpStr):
    def process(self, dev):
        try:
            size = os.write(dev.fd, self.data)  
        except OSError as excpt:
            self.process_error(dev, excpt)
        else:
            self.data = self.data[size:]

class DumpFile(DumpStr, sock_writer.DumpFile):
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


