"""

"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, core, xmap, build, make, HttpRequestHandle, InvalidRequest
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
    response = Response()
    response.set_response('HTTP/1.1 200 OK')

    HTML = render('view.jinja', posts = DB.iterkeys())
    response.add_data(HTML)

    send_response(con, response)

@app.route('GET /load_index')
def load_index(con, index):
    response = Response()
    response.set_response('HTTP/1.1 200 OK')
    response.add_header(('Content-Type', 'image/jpeg'))

    response.add_data(DB[index[0]])
    send_response(con, response)

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




