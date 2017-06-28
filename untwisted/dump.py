from untwisted.wrappers import spawn
from untwisted.errors import CLOSE_ERR_CODE
from untwisted.event import CLOSE, SEND_ERR
import socket

class Dump(object):
    def process_error(self, spin, err):
        if err in CLOSE_ERR_CODE: 
            spawn(spin, CLOSE, err)
        else: 
            spawn(spin, SEND_ERR, err)

class DumpStr(Dump):
    __slots__ = 'data'

    def __init__(self, data=''):
        self.data = buffer(data)

    def process(self, spin):
        try:
            size = spin.send(self.data)  
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

    def __nonzero__(self):
        return bool(self.data)

class DumpFile(DumpStr):
    __slots__ = 'fd'
    BLOCK     = 1024 * 124

    def __init__(self, fd):
        self.fd = fd
        DumpStr.__init__(self)
        self.process_file()

    def process(self, spin):
        DumpStr.process(self, spin)

        if not self.data: self.process_file()

    def process_file(self):
        try:
            data = self.fd.read(DumpFile.BLOCK)
        except IOError as e:
            spawn(spin, READ_ERR, e)
        else:
            self.data = buffer(data)



