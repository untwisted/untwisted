""" Author: Jayrays
    Description: A simple port scan that verifies for listening sockets.
"""

from untwisted.network import *
from untwisted.utils.stdio import Client, lose, CONNECT, CONNECT_ERR
from socket import *
from sys import argv

script, ip, low, high = argv

def is_open(spin, port):
    print 'Port %s is open.' % port

for ind in range(int(low), int(high)):
    sock = socket(AF_INET, SOCK_STREAM)
    spin = Spin(sock)
    Client(spin)
    xmap(spin, CONNECT, is_open, ind)
    xmap(spin, CONNECT_ERR, lambda con, err: lose(con))
    xmap(spin, CONNECT, lose)
    spin.connect_ex((ip, ind))


core.gear.mainloop()
