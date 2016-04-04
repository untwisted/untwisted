""" 
"""

from untwisted.network import core, Spin, xmap
from untwisted.iostd import Client, lose, CONNECT, CONNECT_ERR
from untwisted.task import Task, DONE
from untwisted.network import die
from socket import *

def is_open(spin, port):
    print 'Port %s is open.' % port

def create_connection(addr, port):
    sock = socket(AF_INET, SOCK_STREAM)
    spin = Spin(sock)
    Client(spin)
    xmap(spin, CONNECT, is_open, port)
    spin.connect_ex((addr, port))
    return spin

def scan(addr, min, max):
    task = Task()
    for ind in xrange(min, max):
        task.add(create_connection(addr, ind), CONNECT, CONNECT_ERR)
    
    xmap(task, DONE, lambda task: die())

if __name__ == '__main__':
    from optparse import OptionParser
    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr", metavar="string", default='localhost')
    parser.add_option("-x", "--max", dest="max", metavar="integer", default=9999)
    parser.add_option("-n", "--min", dest="min", metavar="integer", default=70)

    (opt, args) = parser.parse_args()
    scan(opt.addr, int(opt.min), int(opt.max))
    core.gear.mainloop()
    








