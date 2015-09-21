"""
"""

from untwisted.plugins.requests import HttpClient, HTTP_RESPONSE, get, auth
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client, LOAD, DUMPED
from untwisted.network import Spin, xmap, core, die
import sys

def connect(rsc, username, password):
    ADDR   = 'baas.kinvey.com'
    PORT   = 80
    HEADER = {
    'Host':'%s' % ADDR,
    'Authorization': auth(username, password)
    }
        
    con  = Spin()
    data = get(rsc, header=HEADER)
    
    Client(con)
    con.connect_ex((ADDR, PORT))

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
    die()

if __name__ == '__main__':
    con = connect(sys.argv[1], sys.argv[2], sys.argv[3])
    core.gear.mainloop()



