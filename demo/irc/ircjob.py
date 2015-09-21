""" Name: ircjob
    Description: This script connects to an irc network
    authenticates with the server and sends a sequence of commands
    when the 376(End of motd) event happens and closes. It connects
    continuously with intervals of time pre defined.
    Obs: You could use it to send a !keep shell_account on #bzshellz
    at freenode. You just need to change some points.
"""

# It imports basic untwisted objects.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
# The untwisted schedule event.
from untwisted.task import sched  
from untwisted.plugins.irc import *
from socket import socket
# We need it to delay when sending irc commands
# otherwise we can go down by excess of flood.
from time import sleep

def main(address, port, nick, user, cmd, delay=0):
    # It creates our socket object
    # so we wrap it with Spin and install
    # the protocols.
    sock = socket(AF_INET, SOCK_STREAM)
    con = Spin(sock)
    
    # It is the basic client side protocol.
    # We need it to use the CONNECT event.
    Client(con)

    # We don't want an exception so
    # we use connect_ex.
    con.connect_ex((address, port))

    # When the network issues 376(End of motd)
    # we can start sending our commands.
    def do_job(spin, *args):
        for ind in cmd:
            # It sends the command
            # through the socket.
            send_cmd(spin, ind)
            # We need it to avoid excess flood.
            sleep(delay)


    # When con is connected this callback
    # is called. So we authenticate.
    def send_auth(spin):
        # It is used to send data.
        Stdin(con)

        # It is what receives data.
        Stdout(con)
        Shrug(con)

        # It installs the irc protocol.
        Irc(con)

        # We will want to log what is going on.
        logcon(con)
        # This is we map irc events to callbacks.
        xmap(con, '376', do_job)
        xmap(con, 'PING', lambda con, prefix, 
                servaddr: send_cmd(con, 'PONG :%s' % servaddr))

        # When the connection is over we close
        # the socket and call destroy on it.
        # lose does this job and if something went
        # wrong when calling spin.close it spawns
        # CLOSE_ERR event.
        xmap(con, CLOSE, lambda con, err: lose(con))
        print 'sending nick', nick
        send_cmd(spin, 'NICK %s' % nick)
        send_cmd(spin, 'USER %s' % user)
    


    # When CONNECT is issued we have send_auth called.
    xmap(con, CONNECT, send_auth)

    return con

if __name__ == '__main__':
    USER = 'uxirc beta gama :uxirc'
    NICK = 'alpha'
    CMD = ('JOIN #~math',
           'PRIVMSG #~math :Uriel',
           'quit')
    
    INTERVAL = 10
    # This call back will be called periodically.
    cbck = lambda :main('irc.freenode.com', 6667, NICK, USER, CMD)

    sched.after(INTERVAL, cbck, False)

    # it runs the reactor.
    core.gear.mainloop()



