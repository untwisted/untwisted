from untwisted.sock_reader import SockReader
from untwisted.event import CLOSE, LOAD
import os

class FileReader(SockReader):
    """
    Used to read data from a Device instance. It spawns LOAD or CLOSE
    events.

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

