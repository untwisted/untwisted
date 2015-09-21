"""

"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, core, xmap, build, make, HttpServer, InvalidRequest
import shelve

DB_FILENAME = 'DB'
DB          = shelve.open(make(__file__, DB_FILENAME))
render      = build(__file__, 'templates', 'view.jinja')

class ImageUpload(object):
    HttpServer.MAX_SIZE = 1024 * 5024

    def __init__(self, con):
        xmap(con, 'GET /', self.send_base)
        xmap(con, 'POST /add_image', self.add_image)
        xmap(con, 'GET /load_index', self.load_index)

    def send_base(self, con, header, fd, data, version):
        response = Response()
        response.set_response('HTTP/1.1 200 OK')

        HTML = render('view.jinja', posts = DB.iterkeys())
        response.add_data(HTML)

        send_response(con, response)

    def load_index(self, con, header, fd, data, version):
        index = data['index'][0]

        response = Response()
        response.set_response('HTTP/1.1 200 OK')
        response.add_header(('Content-Type', 'image/jpeg'))

        response.add_data(DB[index])
        send_response(con, response)

    def add_image(self, con, header, fd, data, version):
        item              = fd['file']
        DB[item.filename] = item.file.read()
        self.send_base(con, header, None, None, version)

if __name__ == '__main__':
    import sys
    app = RapidServ('0.0.0.0', 5000, 50)
    app.add_handle(ImageUpload)
    app.add_handle(InvalidRequest)

    core.gear.mainloop()
    




