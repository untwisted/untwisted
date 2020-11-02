from untwisted.network import xmap, Spin, core
from untwisted.sock_reader import SockReader, LOAD, CLOSE
from socket import socket, AF_INET, SOCK_STREAM
from untwisted.sock_writer import SockWriter
from untwisted.server import Server, ACCEPT
from untwisted.client import lose

import sys

def setup(server, con):
    SockReader(con)
    SockWriter(con)
    xmap(con, CLOSE, lambda con, err: lose(con))
    xmap(con, LOAD, lambda con, data: sys.stdout.write('%s\r\n' % data))

if __name__ == '__main__':    
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='0.0.0.0')
                  
    parser.add_option("-p", "--port", dest="port",
                      type="int", default=1234)

    parser.add_option("-b", "--backlog", dest="backlog",
                      type="int", default=5)

    (opt, args) = parser.parse_args()
    sock   = socket(AF_INET, SOCK_STREAM)
    server = Spin(sock) 
    server.bind((opt.addr, opt.port))
    server.listen(opt.backlog)
    Server(server)
    
    xmap(server, ACCEPT, setup)
    
    core.gear.mainloop()








