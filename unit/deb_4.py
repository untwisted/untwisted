""" deb_4.py 
    Usage: 
"""

from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.task import Task, COMPLETE
import sys
import random
MAX_REQUEST = 10000
PORT = 1234

def on_accept(serv, con):
    Stdin(con)
    Stdout(con)
    
    base = range(0, MAX_REQUEST)
    random.shuffle(base)

    for ind in base:
        con.dump('%s\r\n' % ind)
    
    xmap(con, DUMPED, lose)

def set_up_server():
    sock = socket(AF_INET, SOCK_STREAM)
    serv = Spin(sock)
    
    serv.bind(('', PORT))
    serv.listen(5)
    Server(serv)

    xmap(serv, ACCEPT, on_accept)

def done(task, data):
    print data
    raise Kill

def on_connect(con):
    Stdin(con)
    Stdout(con)
    Shrug(con)
    xmap(con, FOUND, lambda con, data: spawn(con, data, data))
    #xmap(con, FOUND, lambda con, data: sys.stdout.write('%s\n' % data))
    print 'connected' 

    task = Task(dict())
    
    def job(data, event, args):
        base = data.setdefault(event, list())
        base.append(args[1])
        return True

    for ind in xrange(MAX_REQUEST):
        task.gather(con, ('%s' % ind, job)) 

    xmap(task, COMPLETE, done)

def main():
    set_up_server()

    sock = socket(AF_INET, SOCK_STREAM)
    con = Spin(sock)
    Client(con)

    xmap(con, CONNECT, on_connect)
    xmap(con, CONNECT_ERR, on_connect_err)
    con.connect_ex(('localhost', PORT))


def on_connect_err(con, err):
    print 'on_connect_err %s.' % err

if __name__ == '__main__':
    main()
    #install_reactor(core.Select)
    core.gear.mainloop()

