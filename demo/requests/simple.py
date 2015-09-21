"""
This example doesnt use redirection.

Usage:
python addr port resource

Example:
python www.bol.com.br 80 /
"""

from untwisted.plugins.requests import HttpClient, HTTP_RESPONSE, get
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client
from untwisted.network import Spin, xmap, core

def connect(addr, port, rsc):
    HEADER = {
    'Host':'%s' % addr,
    'User-Agent':"uxreq/1.0", 
    'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Connection':'close',
    }
        
    
    con  = Spin()
    data = get(rsc, header=HEADER)
    
    Client(con)
    con.connect_ex((addr, port))
    xmap(con, CONNECT, set_up_con, data)
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    return con

def set_up_con(con, data):
    Stdin(con)
    Stdout(con)
    
    HttpClient(con)
    xmap(con, HTTP_RESPONSE, handle_http_response)
    xmap(con, CLOSE, lambda con, err: lose(con))

    con.dump(data)
    
def handle_http_response(spin, version, code, reason, header, data):
    print 'data', repr(data)
    print 'version', version
    print 'code', code
    print 'header', header

if __name__ == '__main__':
    import sys
    con = connect(sys.argv[1], int(sys.argv[2]), sys.argv[3])
    core.gear.mainloop()

