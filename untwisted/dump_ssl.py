from untwisted.event import SSL_SEND_ERR, CLOSE
from untwisted.dump import DumpStr, DumpFile
import socket
import ssl

class DumpStrSSL(DumpStr):
    def process(self, spin):
        # When ssl.SSLEOFError happens it shouldnt spawn CLOSE
        # because there may exist data to be read.
        # If it spawns CLOSE the socket is closed and no data
        # can be read from.
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
            self.process_error(spin, excpt)
        else:
            self.data = self.data[size:]

class DumpFileSSL(DumpStrSSL, DumpFile):
    pass







