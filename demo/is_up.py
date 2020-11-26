from untwisted.network import SuperSocket
from untwisted.client import Client, CONNECT, CONNECT_ERR
from untwisted.core import die
from untwisted import core
import errno

def on_connect(con, addr, port):
    print('Connected to %s:%s !' % (addr, port))

def on_connect_err(con, err, addr, port):
    print("Failed to connect to %s:%s, errcode " % (addr, port), errno.errorcode[err])

def create_connection(addr, port):
    con = SuperSocket()
    Client(con)
    con.add_map(CONNECT, on_connect, addr, port)
    con.add_map(CONNECT_ERR, on_connect_err, addr, port)
    con.add_map(CONNECT, lambda con: die())
    con.add_map(CONNECT_ERR, lambda con, err: die())
    
    con.connect_ex((addr, port))

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', help='Address')
    parser.add_argument('-p', '--port', type=int, help='Port')
    args = parser.parse_args()

    create_connection(args.addr, args.port)
    core.gear.mainloop()
    





