"""

"""
from untwisted.plugins.rapidserv import HttpClient, HTTP_RESPONSE, post_data, auth
from untwisted.utils.stdio import Stdin, Stdout, CONNECT, CONNECT_ERR, CLOSE, lose, Client, LOAD, DUMPED
from untwisted.network import Spin, xmap, core, die
from rapidserv import RapidServ, send_response, Response, build, make, HttpServer, InvalidRequest, Locate
from utils import kpost

class Backend(object):
    # HttpServer.MAX_SIZE = 1024 * 5024

    def __init__(self, con):
        xmap(con, 'GET /record', self.record)

    def record(self, con, header, fd, data, version):
        REQUEST  = '/appdata/%s/%s' % (data['appkey'][0], data['collection'][0])
        kcon     = kpost(REQUEST, data['username'][0], data['password'][0], data['json'][0])

        def kresponse(kcon, version, code, reason, header, data):
            response = Response()
            response.set_response('HTTP/1.1 200 OK')
            response.add_data(data)
            send_response(con, response)
    
        xmap(kcon, HTTP_RESPONSE, kresponse)
        con.ACTIVE = True

if __name__ == '__main__':
    import sys
    app = RapidServ('0.0.0.0', 5000, 50)
    app.add_handle(Backend)
    app.add_handle(InvalidRequest)
    app.add_handle(Locate, make(__file__, 'static'))

    core.gear.mainloop()
    






