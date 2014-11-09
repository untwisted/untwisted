from untwisted.network import *
from untwisted.utils.stdio import Client, CONNECT, CONNECT_ERR, CLOSE, lose
from untwisted.utils.sslio import *

def main():
    con = Spin()
    con.connect(('irc.freenode.org', 7000))
    Client(con)
    xmap(con, CONNECT, on_connect)

def on_connect(con):
    Handshake(con)

    pass

def on_handshake(con):
    pass

def on_handshake_err(con):
    pass



