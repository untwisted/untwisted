"""
Name: ircbot.py
Description: Ircbot that connects to a network sits on a channel and
sends a string of text 'bar' when one of the channel users send a string of text 'foo'.
"""

# It imports Spin, xmap, and other useful functions.
from untwisted.network import *
# It imports the basic protocols and events.
from untwisted.utils.stdio import Client, Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, LOAD, lose

# It imports a protocol to tokenizer data using a token.
from untwisted.utils.shrug import Shrug, FOUND

# socket lib.
from socket import socket, AF_INET, SOCK_STREAM

# A small implementation of a untwisted protocol for irc protocol.
from irc import Irc
import sys

def on_connect(con):
    # This protocol is responsible by spawning 
    # the event LOAD. It takes care of spawning a CLOSE
    # event when the connection is over.
    Stdout(con)
    
    # This protocol is responsible by installing a dump method
    # into the con instance. It takes care of sending everything
    # that goes through the dump method.
    Stdin(con)


    # This protocol is used to break the stream of data into chunks delimited
    # by '\r\n'. So, if the network sends 'data1\r\ndata2\r\ndata3\r\n' it will
    # spawns three times the event FOUND. It will carry 'data1', 'data2', 'data3'.
    Shrug(con)

    # This untwisted protocol is a tiny implementation of irc protocol.
    # It handles about 80% of the irc events. It is possible to be improved
    # and handle 100% of all irc events.
    Irc(con)

    # We want to print out on the screen all data that comes from the irc server.
    xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\n' % data))

    # When the connection is over we need to destroy the Spin instance. The
    # lose function takes care of doing that for us.
    xmap(con, CLOSE, lambda con, err: lose(con))

    # When the event 'PRIVMSG' happens then we will have our handle
    # on_privmsg called. You could experiment other irc commands.
    xmap(con, 'PRIVMSG', on_privmsg)

    # When the irc server requires us to send back a PONG :server.
    xmap(con, 'PING', on_ping)

    # Our nick.
    con.dump('NICK %s\r\n' % NICK)
    
    con.dump('USER %s %s %s :%s\r\n' % (IRC_X, IRC_Y, IRC_Z, IRC_W))

    # Finally, it joins the channel.
    con.dump('JOIN %s\r\n' % CHANNEL)

def on_ping(con, prefix, addr):
    con.dump('PONG :%s\r\n' % addr)

def on_privmsg(con, prefix, argument):
    target, msg = argument.split(' :')
    
    # It checks whether the target is in fact a channel.
    # It might occur that someone else sent a msg to your bot.
    # In that case if i didn't do this check then the bot would
    # get in loop.
    if target.startswith(' #') and msg.startswith('foo'):
        con.dump('PRIVMSG %s :%s\r\n' % (target, MSG))

if __name__ == '__main__':
    # The ircbot nick.
    NICK = 'untwistedbot'
    # The irc server ip.
    ADDRESS = 'irc.freenode.org'
    # The irc server port.
    PORT = 6667
    # THe channel where the bot will sit on.
    CHANNEL = '#&math'
    
    IRC_X = 'user'
    IRC_Y = 'user'
    IRC_Z = 'user'
    IRC_W = 'user'
    
    # The msg sent when one sends 'foo'.
    MSG = 'bar'
    

    # It creates a socket as usual.
    # It will be used to send/receive data to the irc server.
    sock = socket(AF_INET, SOCK_STREAM)
    
    # We wrap the socket with a Spin instance.
    # When we wrap a socket with this instance
    # it automatically adds the socket to the reactor.
    # It sets the socket to non blocking mode as well.
    # From now on we will not be thinking imperatively.
    con = Spin(sock)

    # It attempts to connect to the network.
    # We have to call connect_ex cause the socket
    # is in blocking mode otherwise it would give us
    # an exception.
    con.connect_ex((ADDRESS, PORT))


    # This protocol spawns CONNECT or CONNECT_ERR.
    Client(con)

    # As i have installed the Client protocol which spawns
    # CONNECT or CONNECT_ERR we can link the on_connect handle
    # to the event CONNECT. When the CONNECT events is spawned
    # inside con then we will have our handle on_connect called.
    xmap(con, CONNECT, on_connect)
    
    # When there is no way of connecting to an ip then this
    # event will be spawned.
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    # This is the reactor loop. When we call this method
    # untwisted reactor sits and starts listening on the
    # sockets which were created.
    core.gear.mainloop()





