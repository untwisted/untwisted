from untwisted.network import xmap, Spin, core
from untwisted.iostd import Client, Stdout, Stdin, CONNECT, DUMPED
from socket import socket, AF_INET, SOCK_STREAM
from untwisted.core import die

def setup(con, msg):
    Stdout(con)
    Stdin(con)
    con.dump(msg)
    xmap(con, DUMPED, lambda con: die('Msg dumped!'))

def create_connection(addr, port, msg):
    sock = socket(AF_INET, SOCK_STREAM)
    con  = Spin(sock)

    Client(con)
    con.connect_ex((addr, port))
    xmap(con, CONNECT, setup, msg)

if __name__ == '__main__':
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='localhost')
                  
    parser.add_option("-p", "--port", dest="port",
                      type="int", default=1234)

    parser.add_option("-m", "--msg", dest="msg",
                      metavar="string")

    (opt, args) = parser.parse_args()
    create_connection(opt.addr, opt.port, opt.msg)
    core.gear.mainloop()




