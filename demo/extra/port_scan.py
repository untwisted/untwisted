""" 
"""

from untwisted.network import core, Spin, xmap
from untwisted.iostd import Client, lose, CONNECT, CONNECT_ERR
from socket import *

def is_open(spin, port):
    print 'Port %s is open.' % port

def scan_range(min, max):
    for ind in range(int(low), int(high)):
        sock = socket(AF_INET, SOCK_STREAM)
        spin = Spin(sock)
        Client(spin)
        xmap(spin, CONNECT, is_open, ind)
        xmap(spin, CONNECT_ERR, lambda con, err: lose(con))
        xmap(spin, CONNECT, lose)
        spin.connect_ex((ip, ind))
    
if __name__ == '__main__':
    from optparse import OptionParser
    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr", metavar="string", default='localhost')
    parser.add_option("-x", "--max", dest="max", metavar="integer", default=40)
    parser.add_option("-n", "--min", dest="min", metavar="integer", default=9999)

    (opt, args) = parser.parse_args()

    core.gear.mainloop()
    


