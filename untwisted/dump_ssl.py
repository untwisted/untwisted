from untwisted.event import SSL_SEND_ERR, CLOSE
from untwisted.dump import DumpStr, DumpFile
import socket
import ssl

class DumpStrSSL(DumpStr):
    def process(self, spin):
        try:
            size = spin.send(self.data)  
        except ssl.SSLWantReadError:
            spin.drive(SSL_SEND_ERR, spin, excpt)
        except ssl.SSLWantWriteError:
            spin.drive(SSL_SEND_ERR, spin, excpt)
        except ssl.SSLEOFError as excpt:
            pass
        except ssl.SSLError as excpt:
            spin.drive(CLOSE, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])
        else:
            self.data = buffer(self.data, size)

class DumpFileSSL(DumpStrSSL, DumpFile):
    pass




