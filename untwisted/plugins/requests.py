from untwisted.iostd import LOAD, CLOSE, CONNECT, CONNECT_ERR, Client, Stdin, Stdout, lose
from untwisted.splits import AccUntil, TmpFile
from untwisted.network import Spin, xmap, spawn, zmap
from untwisted.event import get_event
from urllib import urlencode
from untwisted.plugins import rapidserv
from tempfile import TemporaryFile as tmpfile

DEFAULT_HEADERS = {
    'user-agent':"Untwisted-requests/1.0.0", 
    'accept-charset':'ISO-8859-1,utf-8;q=0.7,*;q=0.7',
    'connection':'close',
    }

class Response(object):
    def __init__(self, data):
        headers                              = data.split('\r\n')
        response                             = headers.pop(0)
        self.version, self.code, self.reason = response.split(' ', 2)
        self.headers                         = rapidserv.Headers(headers)
        self.fd                              = tmpfile('a+')

class HttpTransferHandle(rapidserv.HttpTransferHandle):
    def process_request(self, spin, response, data):
        """
        """

        response = Response(response)
        spawn(spin, HttpTransferHandle.HTTP_TRANSFER, response, data)

class HttpResponseHandle(rapidserv.HttpRequestHandle):
    HTTP_RESPONSE = rapidserv.HttpRequestHandle.HTTP_REQUEST

class HttpCode(object):
    def __init__(self, spin):
        xmap(spin, HttpResponseHandle.HTTP_RESPONSE, self.process)

    def process(self, spin, response):
        pass

def on_connect(spin, request):
    Stdin(spin)
    Stdout(spin)
    AccUntil(spin)
    HttpTransferHandle(spin)

    # It has to be mapped here otherwise HttpTransferHandle.HTTP_RESPONSE
    # will be spawned and response.fd cursor will be at the end of the file.
    xmap(spin, TmpFile.DONE, 
                        lambda spin, fd, data: fd.seek(0))

    HttpResponseHandle(spin)
    xmap(spin, CLOSE, lambda con, err: lose(con))

    spin.dump(request)

def create_connection(addr, port, request):
    con  = Spin()
    Client(con)
    con.connect_ex((addr, port))

    xmap(con, CONNECT,  on_connect, request)
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))
    return con

def get(addr, port, path, args={}, version='HTTP/1.1', headers=DEFAULT_HEADERS):
    args = '?%s' % urlencode(args) if args else ''
    headers['host'] = addr

    data  = 'GET %s%s %s\r\n' % (path, args, version)

    for key, value in headers.iteritems():
        data = data + '%s: %s\r\n' % (key, value)
    data = data + '\r\n'
    spin = create_connection(addr, port, data)
    return spin

def post(addr, port, path, payload={}, version='HTTP/1.1', headers=DEFAULT_HEADERS):
    payload                  = urlencode(payload)
    request                  = 'POST %s %s\r\n' % (path, version)
    # should be fixed the content type thing.
    headers['host'] = addr

    headers['content-type']   = 'application/x-www-form-urlencoded'
    headers['content-length'] = len(payload)

    for key, value in headers.iteritems():
        request = request + '%s: %s\r\n' % (key, value)
    request = request + '\r\n' + payload
    spin    = create_connection(addr, port, request)
    return spin

def auth(username, password):
    from base64 import encodestring
    base = encodestring('%s:%s' % (username, password))
    base = base.replace('\n', '')
    return "Basic %s" % base


