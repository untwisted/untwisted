from untwisted.event import ACCEPT, CONNECT, CONNECT_ERR, CLOSE
from untwisted.network import core, Spin, xmap
from untwisted.splits import Terminator
from untwisted.server import Server
from untwisted.sock_writer import SockWriter
from untwisted.sock_reader import SockReader
from untwisted.client import Client

class IrcHub:
    def __init__(self, server_port, backlog, irc_address, irc_port):
        self.irc_address = irc_address
        self.irc_port    = irc_port

        server = Spin()
        server.bind(('', server_port))
        server.listen(int(backlog))
    
        Server(server)
    
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        irc = Spin()
        Client(irc)
        xmap(irc, CONNECT, self.handle_connect, client)
        xmap(irc, CONNECT_ERR, self.down_connection)

        irc.connect_ex((self.irc_address, self.irc_port))

    def handle_connect(self, irc, client):
        SockWriter(client)
        SockReader(client)
        Terminator(client, delim=b'\r\n')
        SockWriter(irc)
        SockReader(irc)
        Terminator(irc, delim=b'\r\n')
        xmap(irc, Terminator.FOUND, self.handle_found)
        xmap(irc, CLOSE, self.down_connection)
        xmap(client, CLOSE, self.down_connection)
        xmap(client, Terminator.FOUND, self.handle_found)

        irc.arrow    = client
        client.arrow = irc

        print('Client Connected', irc.getpeername())
        print('Connection to %s:%s stablished.' % irc.getpeername())


    def down_connection(self, transport, err):
        transport.arrow.destroy()
        transport.arrow.close()
        transport.destroy()
        transport.close()

    def handle_found(self, transport, data):
        transport.arrow.dump(b'%s\r\n' % data)
        print(data)

if __name__ == '__main__':
    import sys

    script, server_port, backlog, target_address, target_port = sys.argv
    IrcHub(int(server_port), int(backlog), target_address, int(target_port))
    core.gear.mainloop()








