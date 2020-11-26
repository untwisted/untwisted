from untwisted.network import SuperSocket
from untwisted.client import Client, CONNECT, CONNECT_ERR
from socket import socket, AF_INET, SOCK_STREAM
from untwisted.task import Task, DONE
from untwisted.core import die
from untwisted import core

def is_open(ssock, port):
    print('Port %s is open.' % port)

def create_connection(addr, port):
    ssock = SuperSocket()
    Client(ssock)
    ssock.add_map(CONNECT, is_open, port)
    ssock.connect_ex((addr, port))
    return ssock

def scan(addr, min, max):
    task = Task()
    for ind in range(min, max):
        task.add(create_connection(addr, ind), CONNECT, CONNECT_ERR)

    task.start()    
    task.add_map(DONE, lambda task: die())

if __name__ == '__main__':
    from optparse import OptionParser
    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr", metavar="string", default='localhost')
    parser.add_option("-x", "--max", dest="max", metavar="integer", default=480)
    parser.add_option("-n", "--min", dest="min", metavar="integer", default=70)

    (opt, args) = parser.parse_args()
    scan(opt.addr, int(opt.min), int(opt.max))
    core.gear.mainloop()
    










