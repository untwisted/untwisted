"""
Name: funchat.py
Description: A simple chat server.

Usage:

    Run the funchat server in /demo/funchat/ with python funchat.py.

    You open two telnet sessions.

    Session 1.
    tau@spin:~/code/untwisted-code/demo/funchat$ telnet '0.0.0.0' 1235
    Trying 0.0.0.0...
    Connected to 0.0.0.0.
    Escape character is '^]'.
    Type a nick.
    Nick:euler
    hey gauss. i heard you are pretty good at maths.
    gauss:i heard you are good too.

    Session 2.
    tau@spin:~/code/untwisted-code/demo/funchat$ telnet '0.0.0.0' 1235
    Trying 0.0.0.0...
    Connected to 0.0.0.0.
    Escape character is '^]'.
    Type a nick.
    Nick:gauss
    euler:hey gauss. i heard you are pretty good at maths.
    i heard you are good too.
"""

# It imports basic objects.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *


class FunChat(object):
    def __init__(self, server):
        # It is basically spin.link.
        xmap(server, ACCEPT, self.handle_accept)
        self.pool = []

    def handle_accept(self, server, client):
        """ When clients connect we are called. """
        NICK_MSG = 'Type a nick.\r\nNick:'
        # Install the basic protocol stdin to send data
        # asynchronously.
        Stdin(client)

        # Install the basic protocol stdout to receive
        # data asynchronously.
        Stdout(client)

        # This protocol works on top of Stdout. 
        # It depends on Stdout events.
        # it generates the event FOUND
        # when it finds a token delimiter
        # in this case the delim is '\r\n'
        # So, whenever the client sends
        # 'This is a msg\r\nThat will split into two
        # lines\r\n' It issues FOUND twice 
        # carrying 'This is a msg' as argument in the first
        # time and 'That will split into two lines' as argument
        # in the second time.
        # Whenever LOAD happens Shrug appends
        # LOAD data argument to its internal buffer
        # in order to expect for a delim.
        Shrug(client, delim='\r\n')
        
        xmap(client, CLOSE, self.handle_close)

        client.dump(NICK_MSG)    
        
        # Wait the FOUND event to be issued again
        # in order to retrieve the nick chosen
        # and install the self.echo_msg handle
        # and add the client to the pool of clients.
        event, args = yield hold(client, FOUND)
        _, nick = args
        
        client.nick = nick 
        xmap(client, FOUND, self.echo_msg)

        self.pool.append(client)

    def echo_msg(self, client, data):
        """ This function echoes msgs through
            the clients connected to the server.
        """
        MSG_SHAPE = '%s:%s\r\n'

        for ind in self.pool:
            if not ind is client:
                ind.dump(MSG_SHAPE % (client.nick, data))

    def handle_close(self, client, err):
        """ I am called when the connection is lost. """

        # It tells untwisted to take this spin off the list
        # for reading, writting sockets.
        client.destroy()

        # Just closes the socket.
        client.close()

        # We no more will echo msgs to this client.
        self.pool.remove(client)

if __name__ == '__main__':
    # We create a Spin class pretty much as we would
    # do with a socket class.
    server = Spin()
    server.bind(('', 1234))
    server.listen(5)


    # Install the Server protocol. This protocol is used
    # When we want to listen for incoming connections. 
    # It generates the ACCEPT event that happens
    # when some client connected.
    Server(server)


    FunChat(server)


    # It processes the clients forever.
    core.gear.mainloop()




