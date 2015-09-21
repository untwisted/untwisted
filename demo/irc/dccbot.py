""" Name:dccbot.py
    Description: It implements a basic dcc file server bot.
    People can send files to the bot and receive files
    from it.
"""

# We import the basic modules.
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.plugins.irc import *
from socket import *
from os.path import getsize, isfile

ADDRESS = 'irc.freenode.org'
PORT = 6667
NICK = 'uxirc'
USER = 'uxirc uxirc uxirc :uxirc'

# The folder where we will be serving files.
FOLDER = '/home/tau/Desktop'

def main():
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
    con.connect_ex((ADDRESS, PORT))
   

    def get_myaddr(con, prefix, nick, msg):
        # This send an irc command in order to
        # receive a reply containing our addr.
            send_cmd(con, 'userhost %s' % nick)
        # It waits till '302' arrives.
            event, args = yield hold(con, '302')
        # Finally we extract our addr.
            myaddr = args[-1].split('@')[1]
            myaddr = gethostbyname(myaddr)
        # We just save our addr to use later
        # in send_file.
            con.myaddr = myaddr     


    def set_up_con(con):
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
        CTCP(con)

        xmap(con, 'PING', lambda con, prefix, servaddr: send_cmd(con, 'PONG :%s' % servaddr))
        xmap(con, '376', lambda con, *args: send_cmd(con, 'JOIN ##calculus'))
    
    # When one issues .send filename port
        xmap(con, 'PRIVMSG', send_file)
    # When one attempts to send a file
    # to the bot it accepts the file.
    # So, we map 'DCC SEND' event to recv_file.
        xmap(con, 'DCC SEND', recv_file)
        xmap(con, '376', get_myaddr)
        xmap(con, CLOSE, lambda con, err: lose(con))

    # We want to print out what is going on.
        logcon(con)

        send_cmd(con, 'NICK %s' % NICK)
        send_cmd(con, 'USER %s' % USER)

    xmap(con, CONNECT, set_up_con) 

def send_file(con, nick, user, host, target, msg):
    """ This function is used to send a file to an user. """
    # This is the ctcp header.
    HEADER = '\001DCC SEND %s %s %s %s\001' 

    # It just accepts requests in private.
    # The request has the form.
    # .send file port
    if msg.startswith('.send') and not target.startswith('#'):
    # It extracts the fields file, port.
        cmd, filename, port = msg.split(' ')
    # The resource which the user wants.
        resource = '%s/%s' % (FOLDER, filename)
    # We need to send the file size with the header.
        size = getsize(resource)
    # It opens the resource for reading.
        fd = open(resource, 'rb')
    # Finally, it creates the socket server to 
    # send the file through.
        back = DccServer(fd, int(port), timeout=50)
    # callback for notification.
        def is_done(back, client, msg):
            """ back is our DccServer instance.
                client is a socket wrapped with
                Spin that is the one receiving
                the file.
            """
            send_msg(con, nick, msg)
            fd.close()
    # It maps our events.
        xmap(back, DONE, is_done, 'Done.')
        xmap(back, CLOSE, lambda back, client, err: is_done(back, client, 'Failed.'))
        xmap(back, ACCEPT_ERR, lambda back, err: is_done(back, None, "Accept error."))
    # TIMEOUT is an event that occurs in the dccsev spin
    # instance not in the client instance.
    # The client instance is the spin instance that is
    # corresponds to the client socket. So, we need to pass
    # None otherwise we get an exception. The None would correspond
    # to client in the position at is_done.
        xmap(back, TIMEOUT, is_done, None, 'TIMEOUT.')    
   # It prepares the header.
        request = HEADER % (filename, 
                            ip_to_long(con.myaddr), 
                            port, 
                            size)

    # it sends. lol.
        send_msg(con, nick, request)

def recv_file(
                con, 
                (
                    nick, 
                    user, 
                    host, 
                    target, 
                    msg,
                ),
                filename,
                address,
                port,
                size
           ):

    resource = '%s/%s' % (FOLDER, filename) 
    # We check if the file already exists.
    if isfile(resource):      
        send_msg(con, nick, 'File already exists.')
    else:
        fd = open(resource, 'wb')
        
        # This is the counter part of DccServer.
        # It is used to receive files.
        back = DccClient(long_to_ip(int(address)), 
                         int(port), fd, int(size)) 

        def is_done(client, msg):
            """ In this case we do not receive
                a back instance since we aren't
                serving a socket.
            """
            send_msg(con, nick, msg)
            fd.close()

        xmap(back, DONE, is_done, 'Done.')
        xmap(back, CLOSE, lambda client, err: is_done(client, 'Failed.'))
        # if it wasn't possible to connect we inform it.
        xmap(back, CONNECT_ERR, lambda client, err: is_done(client, "It couldn't connect."))

if __name__ == '__main__':
    main()
    core.gear.mainloop()

