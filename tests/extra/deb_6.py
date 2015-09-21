""" deb_1.py 
    Usage: Used to test untwisted thread support.
    It starts a connection with a server then the server
    launches threads that waits 3 seconds
    and return a random number. the register
    function returns an ident for the thread
    thats used with cmap to map the ident thread
    to a callback when the thread finishes its task
    and returns a value it calls the functions
    mapped to the thread ident thats a string
    returned by thread.getName().
    the job instance is pretty much a Spin instance
    where events are thread name processes.
"""

from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.job import job
import time

import sys

PORT = 1235

count = 0

def demo(index):
    time.sleep(3)
    return index


def check(job, data, con):
    global count
    con.dump('%s count: %s\r\n' % (data, count))
    count = count + 1

def on_accept(serv, con):
    Stdin(con)
    Stdout(con)
    
    for ind in xrange(1000):
        ident = job.register(demo, ind)
        # Obs i could use xmap but i would have to use zmap again
        # otherwise it would contain a handle that wouldnt be called
        # again. cmap just removes the handle when it is executed once.
        cmap(job, ident, check, con)


def set_up_server():
    sock = socket(AF_INET, SOCK_STREAM)
    serv = Spin(sock)
    
    serv.bind(('', PORT))
    serv.listen(300)
    Server(serv)

    xmap(serv, ACCEPT, on_accept)

def on_connect(con):
    Stdin(con)
    Stdout(con)
    Shrug(con)
    xmap(con, FOUND, lambda con, data: sys.stdout.write('%s\n' % data))
    print 'connected' 

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

