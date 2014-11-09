# Name: foo.py
# Description: This example connects to a local socket it sends
# a chunk of text and disconnects.

from untwisted.network import xmap, Spin, core
from untwisted.utils.stdio import Client, Stdin, CONNECT, DUMPED, lose
from socket import *

def set_up_con(con):
# We install Stdin to be able of sending data.
    Stdin(con)
# When everything is sent it just disconnects.
    xmap(con, DUMPED, lose)

# Stdin installs dump method in con. 
# So, we can use it to send data.
    con.dump('Hello world\r\n')

sock = socket(AF_INET, SOCK_STREAM)
con = Spin(sock)
Client(con)
con.connect_ex(('localhost', 1234))
xmap(con, CONNECT, set_up_con)

core.gear.mainloop()
