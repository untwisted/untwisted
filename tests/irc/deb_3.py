"""
    Name: deb_2.py
    Description: It is a unit test for DccClient, DccServer classes.
    It checkes whether the TIMEOUT event is being spawned correctly.
"""

from untwisted.network import *
from untwisted.event import *
from uxirc.dcc import *
from untwisted.task import sched
from StringIO import StringIO
import sys
logvar = sys.stdout

def run_test(n, m):
    # There will be no transmission
    # of data.
    size = 0
    for ind in xrange(n, m):
        # We will not be ending data
        # so it is empty.
        fd = StringIO() 
        DccServer(fd, ind)
   
    def connect():
        for ind in xrange(n, m):
            fd = StringIO()
            # It will attempt to connect.
            client = DccClient('localhost', ind, fd, size)
            
            # If it fails then the DccServer spawned
            # TIMEOUT correctly and there is no listening socket.
            xmap(client,  
                 CONNECT_ERR, 
                 lambda x, ident=ind: logvar.write('Connection fail %s\n' % ident))
            # If it connects then we have done something wrong.
            xmap(client,  
                 CONNECT, 
                 lambda x, ident=ind: logvar.write('Connected %s\n' % ident))

    # It calls connect after 25 the timeout should run in 20.
    sched.after(25, connect, True)

def main():
    # If it happens connection fail
    # over all the clients then it is
    # fine.
    run_test(1234, 1400)
    gear.mainloop()

main()
