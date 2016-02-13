from untwisted.network import xmap, Spin, core
from untwisted.iostd import Client, Stdin, CONNECT, DUMPED, lose
from socket import socket, AF_INET, SOCK_STREAM
from untwisted.usual import die

def set_up_con(con, msg):
    Stdin(con)
    con.dump(msg)
    xmap(con, DUMPED, lambda con: die())

def create_connection(addr, port, msg):
    sock = socket(AF_INET, SOCK_STREAM)
    con  = Spin(sock)

    Client(con)
    con.connect_ex((addr, port))
    xmap(con, CONNECT, set_up_con, msg)

if __name__ == '__main__':
    from optparse import OptionParser

    parser   = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='localhost')
                  
    parser.add_option("-p", "--port", dest="port",
                      metavar="integer", default=1234)

    parser.add_option("-m", "--msg", dest="msg",
                      metavar="string")

    (opt, args) = parser.parse_args()
    create_connection(opt.addr, opt.port, opt.msg)
    core.gear.mainloop()

