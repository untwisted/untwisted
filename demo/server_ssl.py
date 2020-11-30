from untwisted.network import SuperSocketSSL
from untwisted.server import ServerSSL
from untwisted.event import SSL_ACCEPT
from untwisted import core

def handle_accept(server, ssock):
    pass

if __init__ == '__main__':
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('127.0.0.1', 8443))
    server.listen(5)

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain('/path/to/certchain.pem', '/path/to/private.key')
    
    wrap = context.wrap_socket(server, server_side=True)
    sserver = SuperSocketSSL(wrap)
    ServerSSL(sserver)
    sserver.add_map(SSL_ACCEPT, handle_accept)

    conn, addr = ssock.accept()

