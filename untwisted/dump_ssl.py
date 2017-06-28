from untwisted.event import SSL_SEND_ERR
from untwisted.dump import Dumpfile
import socket
import ssl

class DumpStrSSL(DumpStr):
    def process(self, spin):
        try:
            size = spin.send(self.data)  
        except ssl.SSLError as excpt:
            spawn(spin, SSL_SEND_ERR, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

class DumpFileSSL(DumpStrSSL, DumpFile):
    pass

