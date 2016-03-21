# It imports basic untwisted objects.
from untwisted.network import *
from untwisted.iostd import *
from untwisted.splits import Terminator, logcon
# The untwisted schedule event.
from untwisted.timer import Sched
from untwisted.plugins.irc import *
from socket import socket
# We need it to delay when sending irc commands
# otherwise we can go down by excess of flood.
from time import sleep


def send_auth(con, nick, user, cmd, delay):
    Stdin(con)
    Stdout(con)
    Terminator(con)
    Irc(con)
    logcon(con)

    def do_job(spin, *args):
        for ind in cmd:
            send_cmd(spin, ind)
            sleep(delay)
    
    xmap(con, '376', do_job)
    xmap(con, 'PING', lambda con, prefix, 
            servaddr: send_cmd(con, 'PONG :%s' % servaddr))

    xmap(con, CLOSE, lambda con, err: lose(con))
    send_cmd(con, 'NICK %s' % nick)
    send_cmd(con, 'USER %s' % user)

def main(address, port, nick, user, cmd, delay=1):
    sock = socket(AF_INET, SOCK_STREAM)
    con  = Spin(sock)
    
    Client(con)
    con.connect_ex((address, port))
    xmap(con, CONNECT, send_auth, nick, user, cmd, delay)
    return con

if __name__ == '__main__':
    USER     = 'uxirc beta gama :uxirc'
    NICK     = 'alpha'
    CMD      = ('JOIN #vy','PRIVMSG #vy :Uriel', 'quit')
    INTERVAL = 10
    cbck     = lambda :main('irc.freenode.com', 6667, NICK, USER, CMD)
    Sched(INTERVAL, cbck)

    core.gear.mainloop()




