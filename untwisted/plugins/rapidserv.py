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

from socket import *
from os.path import getsize
from mimetypes import guess_type
from os.path import isfile, join, abspath, basename
from traceback import print_exc as debug
from cStringIO import StringIO
import sys

INVALID_BODY_SIZE = get_event()
IDLE_TIMEOUT      = get_event()
DELIM = '\r\n\r\n'

class RapidServ(object):
    """
    The rapidserv class is used to instantiate the server instance with
    handles.

    Example:

    # The '0.0.0.0' is an interface where to listen for connections.
    # The value 5000 is the port.
    # The value 60 is the backlog.
    app = RapidServ('0.0.0.0', 5000, 60)

    # Handle is any callable object.
    app.add_handle(Handle)

    # Tells untwisted to start processing events.
    core.gear.mainloop()

    """

    def __init__(self, addr, port, backlog):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

        sock.bind((addr, port))
        sock.listen(backlog)

        local = Spin(sock)
        Server(local) 
        
        xmap(local, ACCEPT, self.handle_accept)
        
        # The web apps.
        self.setup = []

    def add_handle(self, handle, *args, **kwargs):
        """
        Handle   - Any callable object.
        *args    - Arguments to be passed to Handle.
        **kwargs - A dict passed to Handle.

        Example:

        class Handle(object):
            def __init__(self, con):
                # xmap is used to map a router to a callback.
                xmap(con, 'GET /', self.on_get)
        
            def on_get(self, con, header, fd, data, version):
                pass

        if __name__ == '__main__':
            app = RapidServ('0.0.0.0', 5000, 60)
            app.add_handle(Simple)
        
        """

        self.setup.append(lambda spin: handle(spin, *args, **kwargs))
    
    def handle_accept(self, local, spin):
        Stdin(spin)
        Stdout(spin)
        AccUntil(spin)
        HttpTransferHandle(spin)
        HttpRequestHandle(spin)
        HttpMethodHandle(spin)
        NonPersistentConnection(spin)

        # spin.add_handle(on_all)
        # xmap(spin, HttpTransferHandle.HTTP_TRANSFER, on_event)
        # xmap(spin, HttpRequestHandle.HTTP_REQUEST, on_event)

        # xmap(spin, TmpFile.DONE, on_event)

        # xmap(spin, AccUntil.DONE, on_event)
        # InvalidRequest(client)

        for ind in self.setup:
            ind(spin)

        xmap(spin, CLOSE, lambda con, err: lose(con))


class Request(object):
    def __init__(self, data):
        headers                              = data.split('\r\n')
        request                              = headers.pop(0)
        self.method, self.path, self.version = request.split(' ')
        self.headers                         = dict(map(self.format_field, headers))

    def format_field(self, data):
        try:
            key, value = data.split(':')
        except ValueError:
            return data, ''
        else:
            return key.lower(), value

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
        xmap(spin, HttpTransferHandle.HTTP_TRANSFER, self.start_data_transfer)

    def start_data_transfer(self, spin, request, data):
        xmap(spin, TmpFile.DONE,  
                   lambda spin, fd, data: spawn(spin, 
                                 HttpRequestHandle.HTTP_REQUEST, request, fd))
        TmpFile(spin, data, int(request.headers.get('content-length', '0')))

class HttpMethodHandle(object):
    def __init__(self, spin):
        xmap(spin, HttpRequestHandle.HTTP_REQUEST, self.process)


    def process(self, spin, request, fd):
        fd = FieldStorage(fp=fd, environ=get_env(request.headers))

        spawn(spin, request.method, request.path, 
                                    request.version, request.headers, fd)
    
        try:
            path, data = request.path.split('?', 1)
        except ValueError:
            spawn(spin, '%s %s' % (request.method, request.path), 
                                 parse_qs(''), request.version, request.headers, fd)
        else:
            spawn(spin, '%s %s' % (request.method, path), 
                                  parse_qs(data), request.version, request.headers, fd)


class NonPersistentConnection(object):
    def __init__(self, spin):
        xmap(spin, DUMPED, lambda con: lose(con))

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
    This handle is used to serve static html.

    Example:

    import sys
    BACKLOG = 50
    app     = RapidServ(sys.argv[1], int(sys.argv[2]), BACKLOG)

    # It will tell Rapidserv to serve html document in a folder
    # under the directory __file__.
    app.add_handle(Locate, make(__file__, 'static'))
    core.gear.mainloop()
    """

    def __init__(self, spin, path):
        xmap(spin, 'GET', self.locate)
        self.path     = abspath(path)

    def locate(self, spin, resource, version, headers, fd):
        path = join(self.path, basename(resource))

        if not isfile(path):
            return

        # This is used to tell rapidserv reactor that 
        # the connection will keep alive to process
        # sending of data.
        spin.ACTIVE = True

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

        drop(spin, path)

        # Wait to dump the file.
        xmap(spin, DUMPED, lose)
        xmap(spin, OPEN_FILE_ERR, lambda con, err: lose(con))


class Header(object):
    """ 
    This class is used to drop header content to the client.
    """
    def __init__(self):
        self.response = ''
        self.header   = dict()
        self.add_header(('Content-Type', 'text/html;charset=utf-8'))
        self.add_header(('Server', 'Rapidserv'))

    def set_response(self, data):
        """ Used to add a http response. """
        self.response = data

    def add_header(self, *args):
        """ 
        Add headers to the http response. 
        """
        for key, value in args:
            self.header[str(key)] = str(value)


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

    spin.ACTIVE = True
    spin.dump(str(response))
    xmap(spin, DUMPED, lambda con: lose(con))

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




