from builtins import object
from untwisted.errors import CLOSE_ERR_CODE, SEND_ERR_CODE
from untwisted.event import CLOSE, SEND_ERR
import socket

class Dump(object):
    def process_error(self, spin, excpt):
        if excpt.args[0] in SEND_ERR_CODE:
            spin.drive(SEND_ERR, excpt)
        elif excpt.args[0] in CLOSE_ERR_CODE: 
            spin.drive(CLOSE, excpt)
        else:
            raise excpt

class DumpStr(Dump):
    __slots__ = 'data'

    def __init__(self, data=b''):
        self.data = memoryview(data)

    def process(self, spin):
        try:
            size = spin.send(self.data)  
        except socket.error as excpt:
            self.process_error(spin, excpt)
        else:
            self.data = self.data[size:]

    def __bool__(self):
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
        except IOError as excpt:
            spin.drive(READ_ERR, excpt)
        else:
            self.data = memoryview(data)







