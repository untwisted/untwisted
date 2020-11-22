from collections import deque
from untwisted.event import DUMPED, WRITE
from untwisted.errors import CLOSE_ERR_CODE, SEND_ERR_CODE
from untwisted.event import CLOSE, SEND_ERR, READ_ERR, SSL_SEND_ERR
import ssl
import socket

class Dump:
    def process_error(self, spin, excpt):
        if excpt.args[0] in SEND_ERR_CODE:
            spin.drive(SEND_ERR, excpt)
        elif excpt.args[0] in CLOSE_ERR_CODE: 
            if not spin.dead:
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

    def process(self, spin):
        if not self.data: 
            self.process_file(spin)
        DumpStr.process(self, spin)

    def process_file(self, spin):
        try:
            data = self.fd.read(DumpFile.BLOCK)
        except IOError as excpt:
            spin.drive(READ_ERR, excpt)
        else:
            self.data = memoryview(data)

class DumpStrSSL(DumpStr):
    def process(self, spin):
        # When ssl.SSLEOFError happens it shouldnt spawn CLOSE
        # because there may exist data to be read.
        # If it spawns CLOSE the socket is closed and no data
        # can be read from.
        try:
            size = spin.send(self.data)  
        except ssl.SSLWantReadError as excpt:
            spin.drive(SSL_SEND_ERR, spin, excpt)
        except ssl.SSLWantWriteError as excpt:
            spin.drive(SSL_SEND_ERR, spin, excpt)
        except ssl.SSLEOFError as excpt:
            pass
        except ssl.SSLError as excpt:
            spin.drive(CLOSE, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt)
        else:
            self.data = self.data[size:]

class DumpFileSSL(DumpStrSSL, DumpFile):
    pass

class SockWriter:
    """ 
    Stdin is a handle used to send data through Spin connections.

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

class SockWriterSSL(SockWriter):
    def dump(self, data):
        self.start()
        data = DumpStrSSL(data)
        self.queue.append(data)

    def dumpfile(self, fd):
        self.start()
        fd = DumpFileSSL(fd)
        self.queue.append(fd)

