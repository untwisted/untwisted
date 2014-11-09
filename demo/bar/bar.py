# Name: bar.py
# Description: It sets a server socket and prints everything 
# the clients send to the server.

from untwisted.network import xmap, Spin, core
from untwisted.utils.stdio import Server, Stdout, lose, ACCEPT, LOAD, CLOSE
from socket import *
import sys

def set_up_con(server, con):
    Stdout(con)
    xmap(con, CLOSE, lambda con, err: lose(con))
    xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\n' % data))
    
sock = socket(AF_INET, SOCK_STREAM)
server = Spin(sock) 
server.bind(('', 1234))
server.listen(2)
Server(server)

xmap(server, ACCEPT, set_up_con)

core.gear.mainloop()
