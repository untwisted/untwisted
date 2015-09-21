""" Name:net.py
    Description: It implements basic functionalities for paquitabot.
"""

# We import the basic modules.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.plugins.irc import Irc
from socket import *

def irc_connect(ip, port, nick, user):
    """ It sets up the bot instance. """
    sock = socket(AF_INET, SOCK_STREAM)

    # We have to wrap our socket with a Spin instance
    # in order to have our events issued when data comes
    # from the socket.
    con = Spin(sock)
    
    # This protocol is required by uxirc.irc protocol.
    # It spawns CONNECT.
    Client(con)


    # We use connect_ex since we do not want an exception.
    # Untwisted uses non blocking sockets.
    con.connect_ex((ip, port))

    def send_auth(con):
        # It is what we use to send data. send_msg function uses
        # spin.dump function to dump commands.
        Stdin(con)

        # Shrug protocols requires Stdout that spawns LOAD
        # when data arrives. 
        Stdout(con)

        # This protocol spawns FOUND whenever it finds \r\n.
        Shrug(con)

        # Finally, uxirc.irc protocol spawns irc events when FOUND
        # is issued.
        Irc(con)


        xmap(con, 'PING', send_pong)
        xmap(con, CLOSE, lambda con, err: lose(con))

        send_cmd(con, 'NICK %s' % nick)
        send_cmd(con, 'USER %s' % user)

    def send_pong(con, prefix, servaddr):
        reply = 'PONG :%s\r\n' % servaddr
        send_cmd(con, reply)

    xmap(con, CONNECT, send_auth)

    return con

