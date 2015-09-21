"""
Usage:
    Run it in untwisted/demo/irchub as python irchub.py
"""

# It imports basic objects.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *

class IrcHub(object):
    """ 
    Used to mirror an irc network.
    """
    def __init__(self, server, irc_address, irc_port):
        self.irc_address = irc_address
        self.irc_port = irc_port
        # It is basically spin.link.
        xmap(server, ACCEPT, self.handle_accept)

    def handle_accept(self, server, client):
        """ When clients connect we are called. """

        # We create the irc connection.

        # We need this protocol.
        # It is what issues CONNECT or CONNECT_ERR.

        """ When the socket connected. """
        Stdin(client)
        # Install the basic protocol stdout to receive
        # data asynchronously.
        Stdout(client)
        Shrug(client, delim='\r\n')

        xmap(client, FOUND, self.handle_found)
        xmap(client, CLOSE, self.down_connection)

        irc = Spin()
        Client(irc)
        Stdin(irc)
        Stdout(irc)
        Shrug(irc, delim='\r\n')
        xmap(irc, FOUND, self.handle_found)
        xmap(irc, CONNECT, self.handle_connect)
        xmap(irc, CONNECT_ERR, self.down_connection)
        xmap(irc, CLOSE, self.down_connection)

        # We save the client instance into irc. 
        # We will need it to delivery msgs.
        irc.arrow = client

        # It is like binding both the clients.
        client.arrow = irc
        
        # Try to connect if it falls just disconnects client.
        irc.connect_ex((self.irc_address, self.irc_port))

    def handle_connect(self, irc):
        """ Called when irc connection is stablished """
        print 'Connection to %s:%s stablished.' % irc.getpeername()


    def down_connection(self, transport, err):
        transport.arrow.close()
        transport.arrow.destroy()
        transport.close()
        transport.destroy()

    def handle_found(self, transport, data):
        """ tranposrt can either be irc or client connections."""

        # We need to add \r\n in order to correctly dump the msgs.
        transport.arrow.dump('%s\r\n' % data)
        

if __name__ == '__main__':
    import sys

    # We create a Spin class pretty much as we would
    # do with a socket class.

    script, server_port, backlog, target_address, target_port = sys.argv

    server = Spin()
    server.bind(('', int(server_port)))
    server.listen(int(backlog))


    # Install the Server protocol. This protocol is used
    # When we want to listen for incoming connections. 
    # It generates the ACCEPT event that happens
    # when some client connected.
    Server(server)

    IrcHub(server, target_address, int(target_port))


    # It processes the clients forever.
    core.gear.mainloop()




