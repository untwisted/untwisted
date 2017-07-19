from builtins import object
from collections import deque
from untwisted.event import DUMPED, WRITE
from untwisted.dump import DumpStr, DumpFile
from untwisted import core

class Stdin(object):
    """ 
    Stdin is a handle used to send data through Spin connections.

    Methods:
        dump     - Send data through the Spin instance.

        dumpfile - Dump a file through the Spin instance.

    Diagram:
        WRITE -> Stdin -(int:err, int:err, ())-> {**CLOSE, SEND_ERR, DUMPED}
    """

    def __init__(self, spin):
        """ 
        """

        self.queue    = deque()
        self.data     = None
        spin.dump     = self.dump
        spin.dumpfile = self.dumpfile
        self.spin     = spin

    def update(self, spin):
        """
        """
        
        if not self.data: 
            self.process_queue(spin)

        self.data.process(spin)

    def process_queue(self, spin):
        try:
            self.data = self.queue.popleft()
        except IndexError: 
            self.stop()

    def stop(self):
        self.spin.del_map(WRITE, self.update)
        self.spin.drive(DUMPED)

    def start(self):
        if not self.queue: 
            self.spin.add_map(WRITE, self.update)

    def dump(self, data):
        """ 
        Send data through a Spin instance. 
        """

        self.start()
        dump = DumpStr(data)
        self.queue.append(dump)

    def dumpfile(self, fd):
        """ 
        Dump a file through a Spin instance. 
        """

        self.start()
        dump = DumpFile(fd)
        self.queue.append(dump)





