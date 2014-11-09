""" deb_5.py 
    Usage: 
"""
from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from untwisted.task import Task, COMPLETE

import sys
import random
MAX_CON = 200
LOW = 0
HIGH = 5

PORT = 1234

def on_accept(serv, con):
    Stdin(con)
    Stdout(con)
    
    cookie = random.randint(LOW, HIGH)
    #print cookie
    con.dump('%s\r\n' % cookie)

    xmap(con, DUMPED, lose)

def set_up_server():
    sock = socket(AF_INET, SOCK_STREAM)
    serv = Spin(sock)
    
    serv.bind(('', PORT))
    serv.listen(300)
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

def main():
    task = Task(dict())
    set_up_server()

  
    for ind in xrange(MAX_CON):
        sock = socket(AF_INET, SOCK_STREAM)
        con = Spin(sock)
        Client(con)

        xmap(con, CONNECT, on_connect)
        xmap(con, CONNECT_ERR, on_connect_err)
        con.connect_ex(('localhost', PORT))

        def job(data, event, args, index=ind):
            base = data.setdefault(event, list())
            base.append(('Con %s' % index, args[1]))
            return True

        task.gather(con, 
                         ('0', job),
                         ('1', job),
                         ('2', job),
                         ('3', job),
                         ('4', job),
                         ('5', job),
                         (CONNECT_ERR, lambda *args: True)) 



    xmap(task, COMPLETE, done)

def on_connect_err(con, err):
    print 'on_connect_err %s.' % err

if __name__ == '__main__':
    main()
    #install_reactor(core.Select)
    core.gear.mainloop()

