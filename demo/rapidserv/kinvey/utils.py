"""
"""

from untwisted.plugins.rapidserv import HttpClient, HTTP_RESPONSE, post_data, auth
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client, LOAD, DUMPED
from untwisted.network import Spin, xmap, core, die
import json
import sys

def kpost(rsc, username, password, payload):
    ADDR   = 'baas.kinvey.com'
    PORT   = 80
    HEADER = {
    'Host':'%s' % ADDR,
    'Authorization': auth(username, password)
    }
        
    con  = Spin()
    data = post_data(rsc, data=json.loads(payload), header=HEADER)
    
    Client(con)
    con.connect_ex((ADDR, PORT))

    xmap(con, CONNECT, set_up_con, data)
    return con

def set_up_con(con, data):
    Stdin(con)
    Stdout(con)
    
    HttpClient(con)
    xmap(con, CLOSE, lambda con, err: lose(con))
    con.dump(data)



