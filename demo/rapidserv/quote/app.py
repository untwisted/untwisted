"""
Description: This file implements a simple quote system using jinja2 template system.

Usage:
python app.py '0.0.0.0' 1025

"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, Locate, DebugGet, core, xmap, build, make
import sqlite3
import os.path

DB_FILENAME = 'DB'
DB          = sqlite3.connect(make(__file__, DB_FILENAME))
render      = build(__file__, 'templates', 'show.jinja', 'view.jinja')
app         = RapidServ()
DB.execute('CREATE TABLE quotes (id  INTEGER PRIMARY KEY, name TEXT, quote TEXT)')
DB.commit()

@app.accept
def setup(con):
    Locate(con, make(__file__, 'static'))

@app.request('GET /')
def send_base(con, request):
    # The http response.
    response = Response()
    response.set_response('HTTP/1.1 200 OK')

    rst  = DB.execute('SELECT * FROM quotes')
    HTML = render('show.jinja', posts = rst.fetchall())

    response.add_data(HTML)
    send_response(con, str(response))

@app.request('GET /load_index')
def load_index(con, request):
    index        = request.query['index']
    rst          = DB.execute('SELECT name, quote FROM quotes where id=?', index)
    name, quote  = rst.fetchone()
    HTML         = render('view.jinja', name=name, quote=quote)
    response     = Response()

    response.set_response('HTTP/1.1 200 OK')
    response.add_data(HTML)

    send_response(con, str(response))

@app.request('GET /add_quote')
def add_quote(con, request):
    name      = request.query['name'][0]
    quote     = request.query['quote'][0]
    DB.execute("INSERT INTO quotes (name, quote) VALUES %s" % repr((name, quote)))
    send_base(con, request)

if __name__ == '__main__':
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-a", "--addr", dest="addr",
                      metavar="string", default='0.0.0.0')
                  
    parser.add_option("-p", "--port", dest="port",
                      metavar="integer", default=80)

    parser.add_option("-b", "--backlog", dest="backlog",
                      metavar="integer", default=50)

    (opt, args) = parser.parse_args()
    app.run(opt.addr, opt.port, opt.backlog)
    

