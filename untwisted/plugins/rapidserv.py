""" 
"""

from untwisted.network import xmap, zmap, core, spawn
from untwisted.iostd import Stdin, Stdout, Server, DUMPED, lose, LOAD, ACCEPT, CLOSE
from untwisted.splits import AccUntil, TmpFile
from untwisted.timer import Timer
from untwisted.event import get_event
from untwisted.debug import on_event, on_all
from untwisted import network

from urlparse import parse_qs
from cgi import FieldStorage
from tempfile import TemporaryFile as tmpfile

from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR
from os.path import getsize
from mimetypes import guess_type
from os.path import isfile, join, abspath, basename, dirname
from jinja2 import Template, FileSystemLoader, Environment, PackageLoader

INVALID_BODY_SIZE = get_event()
IDLE_TIMEOUT      = get_event()
DELIM = '\r\n\r\n'

class Spin(network.Spin):
    def __init__(self, sock, app):
        network.Spin.__init__(self, sock)
        self.app          = app
        self.response     = ''
        self.headers      = dict()
        self.data         = ''
        self.add_default_headers()

    def add_default_headers(self):
        self.set_response('HTTP/1.1 200 OK')
        self.add_header(('Server', 'Rapidserv'))

    def set_response(self, data):
        self.response = data

    def add_header(self, *args):
        for key, value in args:
            self.headers[str(key).lower()] = str(value)

    def add_data(self, data, mimetype='text/html;charset=utf-8'):
        self.add_header(('Content-Type', mimetype))
        self.data = str(data)

    def done(self):
        self.headers['Content-Length'] = len(self.data)
        self.send_headers()
        self.dump(self.data)
        self.add_default_headers()
        self.data = ''
        self.response = ''

    def send_headers(self):
        """
        """

        data = self.response
        for key, value in self.headers.iteritems():
            data = data + '\r\n' + '%s:%s' % (key, value)
        data = data + '\r\n\r\n'
        self.dump(data)

    def render(self, template):
        pass

class RapidServ(object):
    """
    """

    def __init__(self, app_dir, static_dir='static', template_dir='templates'):
        self.app_dir      = dirname(abspath(app_dir))
        self.static_dir   = static_dir
        self.template_dir = template_dir
        sock              = socket(AF_INET, SOCK_STREAM)
        self.local        = network.Spin(sock)
        self.local.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

    def bind(self, addr, port, backlog):
        Server(self.local, lambda sock: Spin(sock, self)) 
        self.local.bind((addr, port))
        self.local.listen(backlog)
        
        xmap(self.local, ACCEPT, self.handle_accept)

    def run(self, addr, port, backlog):
        self.bind(addr, port, backlog)
        core.gear.mainloop()

    def handle_accept(self, local, spin):
        Stdin(spin)
        Stdout(spin)
        AccUntil(spin)
        HttpTransferHandle(spin)
        HttpRequestHandle(spin)
        HttpMethodHandle(spin)

        # must be improved.
        Locate(spin)

        NonPersistentConnection(spin)

        # PersistentConnection(spin)
        # InvalidRequest(client)

        xmap(spin, CLOSE, lambda con, err: lose(con))

    def route(self, method):
        """
        """

        def shell(handle):
            xmap(self.local, ACCEPT, lambda local, spin: 
                 xmap(spin, method, self.build_kw, handle))
            return handle
        return shell

    def request(self, method):
        """
        """

        def shell(handle):
            xmap(self.local, ACCEPT, lambda local, spin: 
                 xmap(spin, method, handle))
            return handle
        return shell

    def build_kw(self, spin, request, handle):
        """
        """

        kwargs = dict()
        kwargs.update(request.query)

        if request.data: 
            kwargs.update(request.data)
        handle(spin, **kwargs)

    def accept(self, handle):
        xmap(self.local, ACCEPT, lambda local, spin: handle(spin))

class Request(object):
    def __init__(self, data):
        headers                              = data.split('\r\n')
        request                              = headers.pop(0)
        self.method, self.path, self.version = request.split(' ')
        self.headers                         = dict(map(self.split_field, headers))
        self.fd                              = tmpfile('a+')
        self.data                            = None
        self.path, sep, self.query           = self.path.partition('?')
        self.query                           = parse_qs(self.query)

    def build_data(self):
        self.fd.seek(0)
        self.data = FieldStorage(fp=self.fd, environ=get_env(self.headers))

    def split_field(self, data):
        field, sep, value = data.partition(':')
        return field.lower(), value

class HttpTransferHandle(object):
    HTTP_TRANSFER = get_event()

    def __init__(self, spin):
        xmap(spin, AccUntil.DONE, self.process_request)

    def process_request(self, spin, request, data):
        request = Request(request)
        spawn(spin, HttpTransferHandle.HTTP_TRANSFER, request, data)

class HttpRequestHandle(object):
    HTTP_REQUEST = get_event()
    MAX_SIZE     = 124 * 1024

    def __init__(self, spin):
        self.request = None
        xmap(spin, HttpTransferHandle.HTTP_TRANSFER, self.process)
        xmap(spin, TmpFile.DONE,  
                   lambda spin, fd, data: spawn(spin, 
                                 HttpRequestHandle.HTTP_REQUEST, self.request))

    def process(self, spin, request, data):
        self.request = request
        TmpFile(spin, data, int(request.headers.get('content-length', '0')), request.fd)

class HttpMethodHandle(object):
    def __init__(self, spin):
        xmap(spin, HttpRequestHandle.HTTP_REQUEST, self.process)

    def process(self, spin, request):
        request.build_data()
        spawn(spin, request.method, request)
        spawn(spin, '%s %s' % (request.method, request.path), request)

class NonPersistentConnection(object):
    def __init__(self, spin):
        xmap(spin, DUMPED, lambda con: lose(con))

class PersistentConnection(object):
    def __init__(self, spin, max=10, timeout=120):
        xmap(spin, TmpFile.DONE, lambda con, fd, data: AccUntil(con, data))
        spin.add_header(('connection', 'keep-alive'))
        spin.add_header(('keep-alive', 'timeout=15, max=10'))

class DebugRequest(object):
    def __init__(self, spin):
        xmap(spin, HttpRequestHandle.HTTP_REQUEST, self.process)

    def process(self, spin, request):
        print request.method
        print request.path
        print request.data
        print request.headers

class InvalidRequest(object):
    """ 
    This handle is used to finish a connection
    whose state do not match the constraints.
    """

    def __init__(self, spin):
        xmap(spin, INVALID_BODY_SIZE, self.error)
        xmap(spin, IDLE_TIMEOUT, self.error)

    def error(self, spin):
        spin.set_response('HTTP/1.1 400 Bad request')
        HTML = '<html> <body> <h1> Bad request </h1> </body> </html>'
        spin.add_data(HTML)
        spin.done()

class Locate(object):
    """
    """

    def __init__(self, spin):
        xmap(spin, 'GET', self.locate)

    def locate(self, spin, request):
        path = join(spin.app.app_dir, spin.app.static_dir, basename(request.path))

        if not isfile(path):
            return

        # Where we are going to serve files.
        # I might spawn an event like FILE_NOT_FOUND.
        # So, users could use it to send appropriate answers.
        type_file, encoding = guess_type(path)
        default_type = 'application/octet-stream'

        spin.add_header(('Content-Type', type_file if type_file else default_type),
                     ('Content-Length', getsize(path)))

        spin.send_headers()
        xmap(spin, OPEN_FILE_ERR, lambda con, err: lose(con))
        drop(spin, path)

def get_env(header):
    """
    Shouldn't be called outside this module.
    """

    environ = {
                'REQUEST_METHOD':'POST',
                'CONTENT_LENGTH':header.get('content-length', 0),
                'CONTENT_TYPE':header.get('content-type', 'text')
              }

    return environ


OPEN_FILE_ERR = get_event()
def drop(spin, filename):
    """
    Shouldn't be called outside this module.
    """

    try:
        fd = open(filename, 'rb')             
    except IOError as excpt:
        err = excpt.args[0]
        spawn(spin, OPEN_FILE_ERR, err)
    else:
        spin.dumpfile(fd)


class Jinja2(object):
    def __init__(self, app):
        self.loader   = FileSystemLoader(searchpath = join(app.app_dir, app.template_dir))
        self.env      = Environment(loader=self.loader)
        self.app      = app

    
    def render(self, template_name, *args, **kwargs):
        template = self.env.get_template(template_name)
        return template.render(*args, **kwargs)


def make(searchpath, folder):
    """
    Used to build a path search for Locate plugin.
    """

    from os.path import join, abspath, dirname
    searchpath = join(dirname(abspath(searchpath)), folder)
    return searchpath



