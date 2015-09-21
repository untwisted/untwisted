""" Name: funbot.py
    Description: It connects to an irc network and prints irc events
    when them are issued.
"""

# We import the basic modules.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.plugins.irc import *
from socket import *

class FunBot(object):
    """ Bot class """
    def __init__(self, ip, port, nick, user, password, *chan_list):
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

        # We save whatever we might need.
        self.nick = nick
        self.user = user
        self.password = password
        self.chan_list = chan_list
        self.ip = ip
        self.port = port

        # It maps CONNECT to self.send_auth so
        # when our socket connects it sends NICK and USER info.
        xmap(con, CONNECT, self.send_auth)
        xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    def send_auth(self, con):
        # It is what we use to send data. send_msg function uses
        # spin.dump function to dump commands.
        Stdin(con)

        # Shrug protocols requires Stdout that spawns LOAD
        # when data arrives. 
        Stdout(con)

        # This protocol spawns FOUND whenever it finds \r\n.
        Shrug(con)

        Irc(con)
        
        xmap(con, CLOSE, lambda con, err: lose(con))

        # Now, it basically means: when it '376' irc command is
        # issued by the server then calls self.auto_join.
        # We use auto_join to send the sequence of JOIN
        # commands in order to join channels.
        xmap(con, '376', self.auto_join)

        # Below the remaining stuff follows the same pattern.
        xmap(con, 'JOIN', self.on_join)
        xmap(con, 'PING', self.on_ping)
        xmap(con, 'PART', self.on_part)
        xmap(con, '376', self.on_376)
        xmap(con, 'NOTICE', self.on_notice)
        xmap(con, 'PRIVMSG', self.on_privmsg)
        xmap(con, '332', self.on_332)
        xmap(con, '001', self.on_001)
        xmap(con, '001', self.on_002)
        xmap(con, '003', self.on_003)
        xmap(con, '004', self.on_004)
        xmap(con, '333', self.on_333)
        xmap(con, '353', self.on_353)
        xmap(con, '366', self.on_366)
        xmap(con, '474', self.on_474)
        xmap(con, '302', self.on_302)


        send_cmd(con, 'NICK %s' % self.nick)
        send_cmd(con, 'USER %s' % self.user)
        send_msg(con, 'nickserv', 'identify %s' % self.password)

    def auto_join(self, con, *args):
        for ind in self.chan_list:
            send_cmd(con, 'JOIN %s' % ind)

    def on_ping(self, con, prefix, servaddr):
        # If we do not need pong we are disconnected.
        print 'on_ping', (prefix, servaddr)
        reply = 'PONG :%s\r\n' % servaddr
        send_cmd(con, reply)
        
    def on_join(self, con, nick, user, host, chan):
        print 'on_join\n', (nick, user, host, chan)

    def on_part(self, con, nick, user, host, chan):
        print 'on_part\n', (nick, user, host, chan)

    def on_privmsg(self, con, nick, user, host, target, msg):
        print 'on_privmsg\n', (nick, user, host, target, msg)

    def on_332(self, con, prefix, nick, chan, topic):
        print 'on_332\n', (prefix, nick, chan, topic)

    def on_302(self, con, prefix, nick, info):
        print 'on_302\n', (prefix, nick, info)

    def on_333(self, con, prefix, nick_a, chan,  nick_b, ident):
        print 'on_333\n', (prefix, nick_a, chan, nick_b, ident)

    def on_353(self, con, prefix, nick, mode, chan, peers):
        print 'on_353\n', (prefix, nick, mode, chan, peers)

    def on_366(self, con, prefix, nick, chan, msg):
        print 'on_366\n', (prefix, nick, chan, msg)

    def on_474(self, con, prefix, nick, chan, msg):
        print 'on_474\n', (prefix, nick, chan, msg)

    def on_376(self, con, prefix, nick, msg):
        print 'on_376\n', (prefix, nick, msg)

    def on_notice(self, con, prefix, nick, msg, *args):
        print 'on_notice\n', (prefix, nick, msg), args

    def on_001(self, con, prefix, nick, msg):
        print 'on_001\n', (prefix, nick, msg)

    def on_002(self, con, prefix, nick, msg):
        print 'on_002\n', (prefix, nick, msg)

    def on_003(self, con, prefix, nick, msg):
        print 'on_004\n', (prefix, nick, msg)

    def on_004(self, con, prefix, nick, *args):
        print 'on_004\n', (prefix, nick, args)
    
    def on_005(self, con, prefix, nick, *args):
        print 'on_005', (prefix, nick, args)

bot = FunBot('irc.freenode.com', 6667, 'Fourier1', 'kaus keus kius :kous', '', '##calculus')
core.gear.mainloop()



