"""
"""

from untwisted.plugins.rapidserv import RapidServ, make
import sqlite3

DB_FILENAME = 'DB'
DB          = sqlite3.connect(make(__file__, DB_FILENAME))
app         = RapidServ(__file__)
DB.execute('CREATE TABLE IF NOT EXISTS quotes (id  INTEGER PRIMARY KEY, name TEXT, quote TEXT)')
DB.commit()

@app.request('GET /')
def send_base(con, request):
    rst = DB.execute('SELECT * FROM quotes')
    con.render('show.jinja', posts = rst.fetchall())
    con.done()

@app.request('GET /load_index')
def load_index(con, request):
    index        = request.query['index']
    rst          = DB.execute('SELECT name, quote FROM quotes where id=?', index)
    name, quote  = rst.fetchone()
    con.render('view.jinja', name=name, quote=quote)
    con.done()

@app.request('GET /add_quote')
def add_quote(con, request):
    name      = request.query['name'][0]
    quote     = request.query['quote'][0]
    DB.execute("INSERT INTO quotes (name, quote) VALUES %s" % repr((name, quote)))
    DB.commit()
    send_base(con, request)

if __name__ == '__main__':
    app.run()
    

