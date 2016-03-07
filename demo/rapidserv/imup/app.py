"""

"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, core, xmap, build, make, HttpRequestHandle, InvalidRequest
import shelve

DB_FILENAME = 'DB'
DB          = shelve.open(make(__file__, DB_FILENAME))
render      = build(__file__, 'templates', 'view.jinja')

class ImageUpload(object):
    HttpRequestHandle.MAX_SIZE = 1024 * 5024

    def __init__(self, con):
        xmap(con, 'GET /', self.send_base)
        xmap(con, 'POST /add_image', self.add_image)
        xmap(con, 'GET /load_index', self.load_index)

    def send_base(self, con, data, version, header, fd):
        response = Response()
        response.set_response('HTTP/1.1 200 OK')

        HTML = render('view.jinja', posts = DB.iterkeys())
        response.add_data(HTML)

        send_response(con, response)

    def load_index(self, con, data, version, header, fd):
        index = data['index'][0]

        response = Response()
        response.set_response('HTTP/1.1 200 OK')
        response.add_header(('Content-Type', 'image/jpeg'))

        response.add_data(DB[index])
        send_response(con, response)

    def add_image(self, con, data, version, header, fd):
        item              = fd['file']
        DB[item.filename] = item.file.read()
        self.send_base(con, None, None, None, None)

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

    app = RapidServ(opt.addr, opt.port, opt.backlog)
    app.add_handle(ImageUpload)
    app.add_handle(InvalidRequest)

    core.gear.mainloop()
    









