"""

"""

from untwisted.plugins.rapidserv import RapidServ, build, make, HttpRequestHandle, InvalidRequest
import shelve

DB_FILENAME = 'DB'
DB          = shelve.open(make(__file__, DB_FILENAME))
render      = build(__file__, 'templates', 'view.jinja')
HttpRequestHandle.MAX_SIZE = 1024 * 5024

app = RapidServ()

@app.accept
def setup(con):
    InvalidRequest(con)

@app.route('GET /')
def index(con):
    HTML = render('view.jinja', posts = DB.iterkeys())
    con.add_data(HTML)
    con.done()

@app.route('GET /load_index')
def load_index(con, index):
    con.add_data(DB[index[0]], mimetype='image/jpeg')
    con.done()

@app.route('POST /add_image')
def add_image(con, file):
    DB[file.filename] = file.file.read()
    index(con)

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


