from untwisted.network import SSL
from untwisted.client import Client
from untwisted.exceptions import Erase
from untwisted.event import WRITE, SSL_CERTIFICATE_ERR, \
SSL_CONNECT_ERR, SSL_CONNECT, CLOSE
import socket
import ssl

class Handshake(object):
    """ 
    """

    def __init__(self, spin):
        spin.add_map(WRITE, self.do_handshake)

    def do_handshake(self, spin):
        """
        """

        try:
            spin.do_handshake()
        except ssl.CertificateError as excpt:
            spin.drive(SSL_CERTIFICATE_ERR, excpt)
        except ssl.SSLWantReadError:
            pass
        except ssl.SSLWantWriteError:
            pass
        except socket.error as excpt:
            # It means the host closed when doing handshake.
            # I need to better check it though.
            spin.drive(CLOSE, excpt)
        except ssl.SSLError as excpt:
            spin.drive(SSL_CONNECT_ERR, excpt)
        else:
            spin.drive(SSL_CONNECT)
            raise Erase

class ClientSSL(Client):
    def update(self, spin):
        Client.update(self, spin)
        Handshake(spin)





