"""
This example post code onto codepad.org.
Usage:
python codepad.py filename

Example
python codepad.py /home/tau/vimperator-keys.html
"""

from untwisted.plugins.requests import HttpClient, HTTP_RESPONSE, post_data
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client
from untwisted.network import Spin, xmap, core, die


def set_up_con(con, data):
    Stdin(con)
    Stdout(con)
    
    HttpClient(con)
    xmap(con, HTTP_RESPONSE, handle_http_response)
    xmap(con, CLOSE, lambda con, err: lose(con))

    con.dump(data)
    
def handle_http_response(spin, version, code, reason, header, data):
    print 'URL:%s' % header['Location']
    die()

if __name__ == '__main__':
    import sys
    fd   = open(sys.argv[1], 'r')
    code = fd.read()
    fd.close()

    ADDR = 'codepad.org'    
    PORT = 80

    HEADER = {
    'Host':ADDR,
    'User-Agent':"uxreq/1.0", 
    'Accept-Charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'Connection':'close',
    }


    PARAMS = {
                    'code':code,
                    'lang':'Plain Text',
                    'submit':'Submit'
               }

    con  = Spin()

    Client(con)
    con.connect_ex((ADDR, PORT))

    xmap(con, CONNECT, set_up_con, post_data('/', data=PARAMS, header=HEADER))
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    core.gear.mainloop()



