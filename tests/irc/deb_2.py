"""
    Name: deb_2.py
    Description: It is a unit test for DccClient, DccServer classes.
    It creates DccServer instances for sending files
    and DccClient instances for receiving files
    it checkes whether the data was sent correctly
    through the localhost interface.
"""

from untwisted.network import *
from untwisted.event import *
from untwisted.plugins.irc import *
from StringIO import StringIO
import sys
logvar = sys.stdout

def check(client, fd, data, ident):
    fd.seek(0)
    chunk = fd.read() 
    if chunk == data:
        logvar.write('Passed %s\n' % ident)
    else:
        logvar.write('Failed %s\n' % ident)

def run_test(n, m, data):
    size = len(data)
     
    for ind in xrange(n, m):
        # It creates a copy of data
        # that is wrapped with StringIO
        # so it behaves like a file.
        fd = StringIO(data) 
        # It is like receiving a file on a port
        # whose value is ind.
        DccServer(fd, ind)
    
    for ind in xrange(n, m):
        fd = StringIO()
        # It tries to connect to the port.
        client = DccClient('localhost', ind, fd, size)
        # When DONE is spawned we check for data corruption.
        xmap(client,  DONE, check, fd, data, ind)

def main():
    # It is like sending 1400 - 1234 files of 4 * 100000 size
    # and receiving the same amount of data.
    # If it when DONE is issued it checkes
    # if it received exactly what it sent.
    run_test(1234, 1400, 'abcd' * 100000)
    gear.mainloop()

main()

