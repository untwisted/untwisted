"""
"""

from untwisted.network import core, Spin, xmap
from untwisted.iostd import *
from untwisted.splits import Terminator

class IrcHub(object):
    def __init__(self, server_port, backlog, irc_address, irc_port):
        self.irc_address = irc_address
        self.irc_port    = irc_port

        server = Spin()
        server.bind(('', server_port))
        server.listen(int(backlog))
    
        Server(server)
    
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        Stdin(client)
        Stdout(client)
        Terminator(client, delim='\r\n')

        xmap(client, Terminator.FOUND, self.handle_found)
        xmap(client, CLOSE, self.down_connection)

        irc = Spin()
        Client(irc)
        Stdin(irc)
        Stdout(irc)
        Shrug(irc, delim='\r\n')
        xmap(irc, Terminator.FOUND, self.handle_found)
        xmap(irc, CONNECT, self.handle_connect)
        xmap(irc, CONNECT_ERR, self.down_connection)
        xmap(irc, CLOSE, self.down_connection)

        irc.arrow    = client
        client.arrow = irc
        
        irc.connect_ex((self.irc_address, self.irc_port))

    def handle_connect(self, irc):
        print 'Connection to %s:%s stablished.' % irc.getpeername()


    def down_connection(self, transport, err):
        transport.arrow.close()
        transport.arrow.destroy()
        transport.close()
        transport.destroy()

    def handle_found(self, transport, data):
        transport.arrow.dump('%s\r\n' % data)
        print data

if __name__ == '__main__':
    import sys

    script, server_port, backlog, target_address, target_port = sys.argv
    IrcHub(int(server_port), int(backlog), target_address, int(target_port))
    core.gear.mainloop()






