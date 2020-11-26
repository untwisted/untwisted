from untwisted.event import ACCEPT, CONNECT
from untwisted.network import SuperSocket
from untwisted.splits import Terminator
from untwisted.server import Server
from untwisted.sock_writer import SockWriter
from untwisted.sock_reader import SockReader
from untwisted.client import Client
from untwisted import core

class IrcHub:
    def __init__(self, server_port, backlog, irc_address, irc_port):
        self.irc_address = irc_address
        self.irc_port    = irc_port

        server = SuperSocket()
        server.bind(('', server_port))
        server.listen(int(backlog))
    
        Server(server)
        server.add_map(ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        irc = SuperSocket()
        Client(irc)
        irc.add_map(CONNECT, self.handle_connect, client)
        irc.connect_ex((self.irc_address, self.irc_port))

    def handle_connect(self, irc, client):
        SockWriter(client)
        SockReader(client)
        Terminator(client, delim=b'\r\n')
        SockWriter(irc)
        SockReader(irc)
        Terminator(irc, delim=b'\r\n')
        irc.add_map(Terminator.FOUND, self.handle_found)
        client.add_map(Terminator.FOUND, self.handle_found)

        irc.arrow    = client
        client.arrow = irc

        print('Client Connected', irc.getpeername())
        print('Connection to %s:%s stablished.' % irc.getpeername())

    def handle_found(self, transport, data):
        transport.arrow.dump(b'%s\r\n' % data)
        print(data)

if __name__ == '__main__':
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-s", "--sport", dest="sport", metavar="integer", default=6667)
    parser.add_option("-p", "--dport", dest="dport", metavar="integer", default=443)
    parser.add_option("-b", "--backlog", dest="backlog", metavar="integer", default=5)

    parser.add_option("-t", "--target", dest="target",
                      metavar="string", default="irc.undernet.org")
    (opt, args) = parser.parse_args()

    IrcHub(int(opt.sport), int(opt.backlog), opt.target, int(opt.dport))
    core.gear.mainloop()








