""" Name:net.py
    Description: It demonstrates how to connect to more than one network.
"""

# We import the basic modules.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.plugins.irc import *
from socket import *

def new_con(ip, port, nick, user, *chan_list):
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

    #To log all msgs.
        logcon(con)

        xmap(con, CLOSE, lambda con, err: lose(con))

        send_cmd(con, 'NICK %s' % nick)
        send_cmd(con, 'USER %s' % user)

    def send_pong(con, prefix, servaddr):
        reply = 'PONG :%s\r\n' % servaddr
        send_cmd(con, reply)

    def auto_join(con, *args):
        for ind in chan_list:
            send_cmd(con, 'JOIN %s' % ind)

    xmap(con, CONNECT, send_auth)
    xmap(con, 'PING', send_pong)
    xmap(con, '376', auto_join)

    return con


NICK_LIST = ('alphaaaa',)

# To not connect too fast.

for ind in NICK_LIST:
    new_con('irc.freenode.org', 6667, ind, 'ae eu de :uxirc', '#vy')

core.gear.mainloop()


