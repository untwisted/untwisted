"""
Description: This file implements a simple quote system using jinja2 template system.

Usage:
python app.py '0.0.0.0' 1025

"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, Locate, DebugGet, core, xmap, build, make
import shelve

DB_FILENAME = 'DB'
DB          = shelve.open(make(__file__, DB_FILENAME))
render      = build(__file__, 'templates', 'show.jinja', 'view.jinja')

class QuoteHandle(object):
    MAX_LENGTH = 30

    def __init__(self, con):
        # Used to map a handle to a route.
        xmap(con, 'GET /', self.send_base)
        xmap(con, 'GET /load_index', self.load_index)
        xmap(con, 'GET /add_quote', self.add_quote)

    def send_base(self, con, header, fd, data, version):
        # The http response.
        response = Response()
        response.set_response('HTTP/1.1 200 OK')

        HTML = render('show.jinja', posts = DB.iteritems())

        # Add a body.
        response.add_data(HTML)

        send_response(con, str(response))
    
    def load_index(self, con, header, fd, data, version):
        index        = data['index'][0]
        name, quote  = DB[index]
        HTML         = render('view.jinja', name=name, quote=quote)
        response     = Response()

        response.set_response('HTTP/1.1 200 OK')
        response.add_data(HTML)

        send_response(con, str(response))

    def add_quote(self, con, header, fd, data, version):
        name      = data['name'][0]
        quote     = data['quote'][0]
        index     = str(len(DB))
        DB[index] = (name, quote)

        self.send_base(con, header, fd, data, version)

if __name__ == '__main__':
    import sys
    BACKLOG = 50
    app     = RapidServ(sys.argv[1], int(sys.argv[2]), BACKLOG)

    app.add_handle(QuoteHandle)
    app.add_handle(Locate, make(__file__, 'static'))
    app.add_handle(DebugGet)
    core.gear.mainloop()
    



