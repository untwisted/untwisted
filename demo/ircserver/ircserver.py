""" This is a small ircserver. 
    Usage:
        python3 ircserver.py
        
    The server will sleep forever handling clients.
"""

from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from socket import *
from rep import *

import servcmd

# Irc response parameters.
IRC_SERVER   = 'heaven.client'
CHANNEL      = '#untwisted'
USER         = 'irc'
HOST         = 'client'
MSG_001      = 'Welcome to untwisted demo irc server.'
MSG_366      = 'End of motd.'


class IrcServer(object):
    def __init__(self, port):
        sock =  socket(AF_INET, SOCK_STREAM)
        sock.bind(('0.0.0.0', port))
        sock.listen(5)

        self.server = Spin(sock)

        setup(self.server, Server)

        xmap(self.server, ACCEPT, self.handle_accept)

        self.pool = {}

    def handle_accept(self, server, client):
        """ Deal with the incoming connections. """
        setup(client, Stdin)
        setup(client, Stdout)
        setup(client, Shrug)

        servcmd.install(client)

        xmap(client, 'NICK', self.handle_nick)
        xmap(client, 'PRIVMSG', self.handle_privmsg)
        xmap(client, CLOSE, self.handle_quit)
        xmap(client, LOAD, self.handle_buffer)
 
    def send_cmd(self, client, data):
        """ A simple function that sends a shaped
            msg format.
        """
        cmd = '%s\r\n' % data

        client.send(cmd)

    def echo(self, data, exclude=[]):
        """ It echoes the clients cmd through
            the pool.
        """
        for ind in self.pool.keys():
            if not ind in exclude:
                self.send_cmd(ind, data)

    def enlist(self):
        """ It returns a list of users in the main channel. """
        nicks = self.pool.values()
        return ' '.join(nicks)

    def drop_client(self, client, cmd):
        """ Drop a client when it didnt pick up
            a nick
        """
        self.send_cmd(client, cmd)
        client.destroy()
        client.close()

    def send_header(self, client, nick):
        """ Send basic headers needed by irc clients. """
        cmdO = REP_NUMERIC_001 % (IRC_SERVER, nick, MSG_001)
        self.send_cmd(client, cmdO)

        cmdZ = REP_NUMERIC_366 % (IRC_SERVER, nick, MSG_366)
        self.send_cmd(client, cmdZ)

        cmdX = REP_JOIN % (nick, USER, HOST, CHANNEL)
        self.echo(cmdX)

        cmdY = REP_NUMERIC_353 % (IRC_SERVER, nick, CHANNEL, self.enlist())
        self.send_cmd(client, cmdY)

    def handle_nick(self, client, nick):
        """ When one issues the nick new_nick
            command.
        """
        if client in self.pool.keys():
            return

        if not (nick in self.pool.values()):
            self.pool[client] = nick
            self.send_header(client, nick)
        else:
            cmd = ':Nick being used.'
            self.drop_client(client, cmd)

    def handle_privmsg(self, client, target, msg):

        """ When one sends a msg just echoes it through
            the pool.
        """
        nick = self.pool[client]

        cmd = REP_PRIVMSG % (nick, USER, HOST, target, msg)
        self.echo(cmd, [client])


    def handle_quit(self, client, err):
        """ If one quit just echoes the quit msg. """
        client.destroy()

        nick = self.pool[client]

        del self.pool[client]

        cmd = REP_QUIT % (nick, USER, HOST, 'Untwisted rocks.')
        self.echo(cmd)

    def handle_buffer(self, client, stack):
        """ It prints all what the server receives.
        It is interesting for debugging.
        """
        print(stack)


if __name__ == '__main__':
    server = IrcServer(6667)
    core.gear.mainloop()

