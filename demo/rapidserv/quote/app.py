"""
"""

from untwisted.plugins.rapidserv import RapidServ, Jinja2, make
import sqlite3

DB_FILENAME = 'DB'
DB          = sqlite3.connect(make(__file__, DB_FILENAME))
app         = RapidServ(__file__)
jinja2      = Jinja2(app)
DB.execute('CREATE TABLE IF NOT EXISTS quotes (id  INTEGER PRIMARY KEY, name TEXT, quote TEXT)')
DB.commit()

@app.request('GET /')
def send_base(con, request):
    rst  = DB.execute('SELECT * FROM quotes')
    con.add_data(jinja2.render('show.jinja', posts = rst.fetchall()))
    con.done()

@app.request('GET /load_index')
def load_index(con, request):
    index        = request.query['index']
    rst          = DB.execute('SELECT name, quote FROM quotes where id=?', index)
    name, quote  = rst.fetchone()
    con.add_data(jinja2.render('view.jinja', name=name, quote=quote))
    con.done()

@app.request('GET /add_quote')
def add_quote(con, request):
    name      = request.query['name'][0]
    quote     = request.query['quote'][0]
    DB.execute("INSERT INTO quotes (name, quote) VALUES %s" % repr((name, quote)))
    DB.commit()
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
    









