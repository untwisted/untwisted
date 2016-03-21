from untwisted.network import *
from untwisted.iostd import Client, Stdin, Stdout, CLOSE, CONNECT, CONNECT_ERR, lose
from untwisted.splits import Terminator, logcon
from untwisted.plugins.irc import Irc, send_cmd
from socket import *

def send_auth(con, nick, user):
    Stdin(con)
    Stdout(con)
    Terminator(con)
    Irc(con)
    logcon(con)

    xmap(con, CLOSE, lambda con, err: lose(con))
    send_cmd(con, 'NICK %s' % nick)
    send_cmd(con, 'USER %s' % user)

def send_pong(con, prefix, servaddr):
    reply = 'PONG :%s\r\n' % servaddr
    send_cmd(con, reply)

def connect(addr, port, nick, user, *chans):
    sock = socket(AF_INET, SOCK_STREAM)
    con  = Spin(sock)
    Client(con)
    con.connect_ex((addr, port))

    def auto_join(con, *args):
        for ind in chans:
            send_cmd(con, 'JOIN %s' % ind)

    xmap(con, CONNECT, send_auth, nick, user)
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))
    xmap(con, 'PING', send_pong)
    xmap(con, '376', auto_join)
    return con

NICK_LIST = ('alphaaaa','cooool', 'blablalb')

for ind in NICK_LIST:
    connect('irc.freenode.org', 6667, ind, 'ae eu de :uxirc', '#vy')

core.gear.mainloop()



