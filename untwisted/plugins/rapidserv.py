""" 
"""

from untwisted.network import *
from untwisted.iostd import Stdin, Stdout, Server, DUMPED, lose, LOAD, ACCEPT, CLOSE
from untwisted.splits import AccUntil, TmpFile
from untwisted.timer import Timer
from untwisted.event import get_event
from untwisted.debug import on_event, on_all
from urlparse import parse_qs
from cgi import FieldStorage
from tempfile import TemporaryFile as tmpfile

from socket import *
from os.path import getsize
from mimetypes import guess_type
from os.path import isfile, join, abspath, basename
from cStringIO import StringIO
from untwisted.network import core

INVALID_BODY_SIZE = get_event()
IDLE_TIMEOUT      = get_event()
DELIM = '\r\n\r\n'

class RapidServ(object):
    """
    """

    def __init__(self):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
        self.local = Spin(sock)

    def bind(self, addr, port, backlog):
        Server(self.local) 
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
        # NonPersistentConnection(spin)
        PersistentConnection(spin)
        # InvalidRequest(client)

        xmap(spin, CLOSE, lambda con, err: lose(con))

    def route(self, method):
        def shell(handle):
            def build(spin, request):
                kwargs = dict()
                kwargs.update(request.query)
                if request.data: 
                    kwargs.update(request.data)
                handle(spin, **kwargs)
            def install(local, spin):
                xmap(spin, method, build)
            xmap(self.local, ACCEPT, install)
            return handle
        return shell

    def accept(self, handle):
        xmap(self.local, ACCEPT, lambda local, spin: handle(spin))

    def request(self, method):
        def shell(handle):
            def install(local, spin):
                xmap(spin, method, handle)
            xmap(self.local, ACCEPT, install)
            return handle
        return shell

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
        xmap(spin, DUMPED, self.stop)

    def stop(self, con):
        try:
            con.destroy()
        except Exception:
            pass
        
        try:
            con.close()
        except Exception:
            pass

class PersistentConnection(object):
    def __init__(self, spin, max=10, timeout=120):
        xmap(spin, TmpFile.DONE, lambda con, fd, data: AccUntil(con, data))

class InvalidRequest(object):
    """ 
    This handle is used to finish a connection
    whose state do not match the constraints.
    """

    def __init__(self, spin):
        xmap(spin, INVALID_BODY_SIZE, self.error)
        xmap(spin, IDLE_TIMEOUT, self.error)

    def error(self, spin):
        response  = Response()
        response.set_response('HTTP/1.1 400 Bad request')
        HTML = '<html> <body> <h1> Bad request </h1> </body> </html>'
        response.add_data(HTML)
        send_response(spin, HTML)

class Locate(object):
    """
    """

    def __init__(self, spin, folder):
        xmap(spin, 'GET', self.locate)
        self.folder = abspath(folder)

    def locate(self, spin, request):
        path = join(self.folder, basename(request.path))

        if not isfile(path):
            return

        # Where we are going to serve files.
        # I might spawn an event like FILE_NOT_FOUND.
        # So, users could use it to send appropriate answers.
        type_file, encoding = guess_type(path)
        default_type = 'application/octet-stream'

        header = Header()
        header.set_response('HTTP/1.1 200 OK')

        header.add_header(('Content-Type', type_file if type_file else default_type),
                     ('Content-Length', getsize(path)))

        # Start sending the header.
        spin.dump(str(header))
        xmap(spin, OPEN_FILE_ERR, lambda con, err: lose(con))
        drop(spin, path)


class Header(object):
    """ 
    This class is used to drop header content to the client.
    """

    default = {}
            
    def __init__(self):
        self.response = ''
        self.header   = dict()
        self.header.update(Header.default)
        self.add_header(('Content-Type', 'text/html;charset=utf-8'))
        self.add_header(('Server', 'Rapidserv'))
        self.add_header(('connection', 'keep-alive'))
        self.add_header(('keep-alive', 'timeout=15, max=10'))
    
    def set_response(self, data):
        """ Used to add a http response. """
        self.response = data

    def add_header(self, *args):
        """ 
        Add headers to the http response. 
        """

        for key, value in args:
            self.header[str(key).lower()] = str(value)

    @staticmethod
    def add_default_header(self, *args):
        for key, value in args:
            Header.default[str(key).lower()] = str(value)

    def __str__(self):
        """
        """

        data = self.response
        for key, value in self.header.iteritems():
            data = data + '\r\n' + '%s:%s' % (key, value)
        data = data + '\r\n\r\n'
        return data

class Response(Header):
    """ 
    This class is used to dump header and body content to the client.
    """
    def __init__(self):
        Header.__init__(self)
        self.data = ''

    def add_data(self, data):
        self.data = self.data + data

    def __str__(self):
        """
        """

        self.header['Content-Length'] = len(self.data)

        x = Header.__str__(self) + self.data 
        return x

class DebugPost(object):
    """
    Used to debug POST calls.
    """

    def __init__(self, spin):
        xmap(spin, 'POST' , self.show_header)

    def show_header(self, spin, header, fd, resource, version):
        print 'POST request handled, ', header, version, resource, fd, spin.getpeername()  


class DebugGet(object):
    """
    Used to debug GET calls.
    """

    def __init__(self, spin):
        xmap(spin, 'GET' , self.show_header)

    def show_header(self, spin, header, fd, resource, version):
        print 'GET request handled, ', header, resource, version, spin.getpeername()   


def send_response(spin, response):
    """
    Used to dump a Response/Header object to the client as well
    as all object whose method __str__ is implemented.
    """

    spin.dump(str(response))

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


def build(searchpath, folder, *args):
    """
    Used to render a template.

    Example:
    
    render is a function that will render the templates show.jinja or view.jinja.

    render = build(__file__, 'templates', 'show.jinja', 'view.jinja')
    
    render('show.jinja', a = 'cool')

    Would render show.jinja with the parameter a = 'cool'.
    """

    from jinja2 import Template, FileSystemLoader, Environment
    from os.path import join, abspath, dirname

    loader        = FileSystemLoader(searchpath = make(searchpath, folder))
    env           = Environment(loader=loader)
    base          = dict(zip(args, map(env.get_template, args)))

    def render(filename, *args, **kwargs):
        return base[filename].render(*args, **kwargs)
    return render

def make(searchpath, folder):
    """
    Used to build a path search for Locate plugin.
    """

    from os.path import join, abspath, dirname
    searchpath = join(dirname(abspath(searchpath)), folder)
    return searchpath







