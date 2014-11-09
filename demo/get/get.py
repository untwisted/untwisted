from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.utils.shrug import *
from urlparse import urlparse
from re import findall, IGNORECASE, compile, search
import sys

LHEADER = get_event()
LBODY = get_event()
DELIM = get_event()
COOKIE_STR = 'set-cookie: (?P<cookie>.*)\r\n'
COOKIE_REG = compile(COOKIE_STR, IGNORECASE)
LOCATION_STR = 'location: (?P<link>.*)\r\n'
LOCATION_REG = compile(LOCATION_STR, IGNORECASE)

class Transfer(object):
    def __init__(self, spin, delim='\r\n\r\n'):
        xmap(spin, LOAD, self.update)
        self.delim = delim

    def update(self, spin, data):
        if self.delim in data: 
            chunk_x, chunk_y = data.split(self.delim, 1)
            zmap(spin, LOAD, self.update)
            spawn(spin, LHEADER, chunk_x)
            spawn(spin, DELIM)
            dum = lambda con, data: spawn(con, LBODY, data)
            xmap(spin, LOAD, dum)
            dum(spin, chunk_y)
        else: 
            spawn(spin, LHEADER, data)


class Header(object):
    def __init__(self, spin):
        xmap(spin, LHEADER, self.update)
        self.data = ''

    def update(self, spin, data):
        self.data = self.data + data
    
    def get_data(self):
        return self.data


def send_header(con, uri, cookies):
    con.dump('GET %s HTTP/1.0\r\n' % uri)
    con.dump('Host: %s\r\n' % urlparse(uri).netloc)
    con.dump('Connection: TE, close\r\n')
    con.dump('User-Agent: UntwistedFile/1.0\r\n')

    for ind in cookies:
        con.dump('Cookie: %s\r\n' % ind)

    con.dump('\r\n')


def create_tunnel(ip, port, uri, cookies):
    sock = socket(AF_INET, SOCK_STREAM)
    con = Spin(sock)
    Client(con)
    
    def send_request(con):
        Stdin(con)
        Stdout(con)
        Transfer(con)
        header = Header(con)
        xmap(con, CLOSE, lambda con, err: lose(con))

        send_header(con, uri, cookies)        
        
        def follow(con):
            data = header.get_data()

            try:
                field = search(LOCATION_REG, data)
                link = field.group('link')
                cookies = findall(COOKIE_REG, data)
                create_tunnel(ip, port, link, cookies)
            except AttributeError:
                xmap(con, LBODY, put)
                xmap(con, CLOSE, lambda con, err: die())

        xmap(con, DELIM, follow)

    xmap(con, CONNECT, send_request)
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))

    con.connect_ex((ip, port))
 


if __name__ == '__main__':
    import sys
    _, ip, port, uri = sys.argv
    port = int(port)
    create_tunnel(ip, port, uri, [])

    core.gear.mainloop()


    # Usage:
    # python get.py 201.47.89.181 3128 http://sourceforge.net/projects/untwisted/files/untwisted-0.1.tar.gz/download >> untwisted.tar.gz
