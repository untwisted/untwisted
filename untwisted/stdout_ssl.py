from untwisted.stdout import Stdout
from untwisted.event import SSL_RECV_ERR
from untwisted.wrappers import spawn
import socket
import ssl

class StdoutSSL(Stdout):
    def update(self, spin):
        try:
            while True:
                self.process_data(spin)
        except ssl.SSLError as excpt:
            spawn(spin, SSL_RECV_ERR, spin, excpt)
        except socket.error as excpt:
            self.process_error(spin, excpt.args[0])


