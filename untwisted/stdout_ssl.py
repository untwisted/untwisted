from untwisted.stdout import Stdout
from untwisted.event import SSL_RECV_ERR, CLOSE
import socket
import ssl

class StdoutSSL(Stdout):
    def update(self, spin):
        try:
            while True:
                self.process_data(spin)
        except ssl.SSLWantReadError as excpt:
            spin.drive(SSL_RECV_ERR, spin, excpt)
        except ssl.SSLWantWriteError as excpt:
            spin.drive(SSL_RECV_ERR, spin, excpt)
        except ssl.SSLError as excpt:
            spin.drive(CLOSE, spin, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt)





