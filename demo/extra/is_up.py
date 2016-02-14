from untwisted.network import core, Spin, xmap, die
from untwisted.iostd import Client, CONNECT, CONNECT_ERR, CLOSE, lose
import errno

def on_connect(con, addr, port):
    print 'Connected to %s:%s !' % (addr, port)

def on_connect_err(con, err, addr, port):
    print "Failed to connect to %s:%s, errcode " % (addr, port), errno.errorcode[err]

def create_connection(addr, port):
    con = Spin()
    Client(con)
    xmap(con, CONNECT, on_connect, addr, port)
    xmap(con, CONNECT_ERR, on_connect_err, addr, port)
    
    xmap(con, CONNECT, lambda con: die())
    xmap(con, CONNECT_ERR, lambda con, err: die())

    con.connect_ex((addr, port))

if __name__ == '__main__':
    import sys
    addr, port = sys.argv[1], int(sys.argv[2])
    create_connection(addr, port)
    core.gear.mainloop()
    


