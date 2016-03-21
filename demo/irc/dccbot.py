"""

"""

# We import the basic modules.
from untwisted.network import *
from untwisted.iostd import *
from untwisted.splits import Terminator, logcon
from untwisted.tools import coroutine
from untwisted.plugins.irc import *
from socket import *
from os.path import getsize, isfile

ADDRESS = 'irc.freenode.org'
PORT = 6667
NICK = 'uxirc'
USER = 'uxirc uxirc uxirc :uxirc'

# The folder where we will be serving files.
FOLDER = '/home/tau/Downloads'

@coroutine
def get_myaddr(con, prefix, nick, msg):
    send_cmd(con, 'userhost %s' % nick)
    args        = yield con, '302'
    _, _, ident = args
    user, myaddr   = ident.split('@')
    con.myaddr  = myaddr

def setup(con):
    Stdin(con)
    Stdout(con)
    Terminator(con)
    Irc(con)
    CTCP(con)

    xmap(con, 'PING', lambda con, prefix, servaddr: send_cmd(con, 'PONG :%s' % servaddr))
    xmap(con, '376', lambda con, *args: send_cmd(con, 'JOIN #ameliabot'))

    xmap(con, 'PRIVMSG', send_file)
    xmap(con, 'DCC SEND', check_file_existence)
    xmap(con, '376', get_myaddr)
    xmap(con, CLOSE, lambda con, err: lose(con))

    logcon(con)

    send_cmd(con, 'NICK %s' % NICK)
    send_cmd(con, 'USER %s' % USER)

def main():
    sock = socket(AF_INET, SOCK_STREAM)
    con  = Spin(sock)

    Client(con)
    con.connect_ex((ADDRESS, PORT))
    xmap(con, CONNECT, setup) 

def send_file(con, nick, user, host, target, msg):
    if not msg.startswith('.send'): 
        return
        
    cmd, filename, port = msg.split(' ')
    resource            = '%s/%s' % (FOLDER, filename)
    size                = getsize(resource)
    fd                  = open(resource, 'rb')

    def is_done(msg):
        send_msg(con, nick, msg)
        fd.close()

    try:
        dcc = DccServer(fd, int(port), timeout=50)
    except Exception:
        is_done('Couldnt list on the port!')
        raise

    xmap(dcc, DONE, lambda *args: is_done('Done.'))
    xmap(dcc, CLOSE, lambda *args: is_done('Failed!'))
    xmap(dcc, ACCEPT_ERR, lambda *args: is_done("Accept error!"))
    xmap(dcc, TIMEOUT, lambda *args: is_done('TIMEOUT!'))    

    HEADER  = '\001DCC SEND %s %s %s %s\001' 
    request = HEADER % (filename, ip_to_long(con.myaddr), port, size)
    send_msg(con, nick, request)

def check_file_existence(con, (nick, user, host, target, msg), 
                                        filename, address, port, size):
    resource = '%s/%s' % (FOLDER, filename) 
    if isfile(resource):      
        send_msg(con, nick, 'File already exists.')
    else:
        recv_file(con, nick, resource, address, port, size)

def recv_file(con, nick, resource, address, port, size):
    fd  = open(resource, 'wb')
    dcc = DccClient(long_to_ip(int(address)), 
                     int(port), fd, int(size)) 

    def is_done(msg):
        send_msg(con, nick, msg)
        fd.close()

    xmap(dcc, DONE, lambda *args: is_done('Done!'))
    xmap(dcc, CLOSE, lambda *args: is_done('Failed!'))
    xmap(dcc, CONNECT_ERR, lambda *args: is_done("It couldn't connect!"))

if __name__ == '__main__':
    # import argparser
    # parser = argparser.ArgumentParser()
    main()
    core.gear.mainloop()


