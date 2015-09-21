""" 
This file implements an abstraction for the http protocol over the server side perspective. 
"""

from tempfile import TemporaryFile as tmpfile
from untwisted.network import *
from untwisted.utils.stdio import Stdin, Stdout, Server, DumpFile, DUMPED, DUMPED_FILE, lose, LOAD, ACCEPT, CLOSE
from untwisted.task import sched
from urlparse import parse_qs
from cgi import FieldStorage

from socket import *
from os.path import getsize
from mimetypes import guess_type
from os.path import isfile, join, abspath, basename
from traceback import print_exc as debug

INVALID_BODY_SIZE = get_event()
IDLE_TIMEOUT      = get_event()

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
    
    def handle_accept(self, local, client):
        """
        This method is not supposed to be called by functions outside
        this class.
        """

        Stdin(client)
        Stdout(client)

        HttpServer(client)
        Get(client)
        Post(client)

        # It serves to determine whether the client made
        # a request whose resource exists.
        # In case it didnt the connection is dropped.
        client.ACTIVE = False

        for ind in self.setup:
            ind(client)

        xmap(client, CLOSE, lambda con, err: lose(con))

class Get(object):
    """ 
    This class shouldn't be used outside this module.
    """

    def __init__(self, spin):
        xmap(spin, 'GET', self.tokenizer)

    def tokenizer(self, spin, header, fd, resource, version):
        """ Used to extract encoded data with get. """
        data = ''

        try:
            resource, data = resource.split('?', 1)
        except ValueError:
            pass

        spawn(spin, 'GET %s' % resource, header, fd,
                                     parse_qs(data), version)

class Post(object):
    """ 
    This class shouldn't be used outside this module.
    """

    def __init__(self, spin):
        xmap(spin, 'POST', self.tokenizer)

    def tokenizer(self, spin, header, fd, resource, version):
        data = ''

        try:
            resource, data = resource.split('?', 1)
        except ValueError:
            pass

        spawn(spin, 'POST %s' % resource, header, 
              FieldStorage(fp=fd, environ=get_env(header)),
                                         parse_qs(data), version)

class HttpServer:
    """ 
    This class shouldn't be used outside this module.
    """

    MAX_SIZE = 124 * 1024
    TIMEOUT  = 16

    def __init__(self, spin):
        self.request  = ''
        self.header   = ''
        self.data     = ''
        self.spin     = spin
        self.fd       = None

        sched.after(self.TIMEOUT, self.spawn_idle_timeout, True)
        xmap(spin, LOAD, self.get_header)

    def spawn_idle_timeout(self):
        spawn(self.spin, IDLE_TIMEOUT)

    def split_header(self, data):
        header  = data.split('\r\n')
        request = header[0].split(' ') 
        del header[0]

        header  = map(lambda x: x.split(': ', 1), header)
        header  = dict(header)
        return request, header

    def get_header(self, spin, data):
        DELIM       = '\r\n\r\n'
        self.header = self.header + data

        if not DELIM in data: return

        header, self.data         = self.header.split(DELIM, 1)
        self.request, self.header = self.split_header(header)

        # So, we have our request.
        # We no more will issue FOUND.
        zmap(spin, LOAD, self.get_header)
        self.check_data_existence()

    def check_data_existence(self):
        try:
            size = self.header['Content-Length']
        except KeyError:
            self.spawn_request()
            return

        self.size = int(size)

        # If self.size is larger than self.MAX_SIZE
        # it spawns INVALID_BODY_SIZE
        # As self.fd.tell() == 0 and self.size > 0
        # xmap(self.spin, LOAD, self.get_data will not be
        # mapped. The body will be empty, no need to drop    
        # the connection here. Permiting clients of the protocol
        # to install handles to deal with this event.
        if self.size > self.MAX_SIZE:
            spawn(self.spin, INVALID_BODY_SIZE)
        else:
            self.wait_for_data()


    def wait_for_data(self):
        try:
            self.fd = tmpfile('a+')
        except Exception:
            debug()
            return

        try:
            self.fd.write(self.data)
        except Exception:
            debug()
            return

        is_done = self.check_data_size()

        if is_done:
            return

        xmap(self.spin, LOAD, self.get_data)

    def spawn_request(self):
        sched.unmark(self.TIMEOUT, self.spawn_idle_timeout)

        spawn(self.spin, self.request[0], self.header, self.fd,
                                    self.request[1], self.request[2])

        if not self.spin.ACTIVE:
            lose(self.spin)

    def check_data_size(self):
        if not self.fd.tell() >= self.size:
            return False

        self.fd.seek(0)
        self.spawn_request()
        self.fd.close()

        return True

    def get_data(self, spin, data):
        """

        """

        try:
            self.fd.write(data)
        except Exception:
            zmap(spin, LOAD, self.get_data)
            debug()

        is_done = self.check_data_size()

        if is_done:
            zmap(spin, LOAD, self.get_data)

        # keep alive connections.
        # self.__init__(self.spin)

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

    def locate(self, spin, header, fd, resource, version):
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

        # Wait to dump the header.
        xmap(spin, DUMPED, lambda con: drop(con, path))

        # Wait to dump the file.

        xmap(spin, DUMPED_FILE, lose)
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

def send_response_wait(spin, response):
    """
    Used to dump content to the client and do not lose the connection.
    """
    pass


def get_env(header):
    """
    Shouldn't be called outside this module.
    """

    environ = {
                'REQUEST_METHOD':'POST',
                'CONTENT_LENGTH':header['Content-Length'],
                'CONTENT_TYPE':header['Content-Type']
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
        DumpFile(spin, fd)



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









