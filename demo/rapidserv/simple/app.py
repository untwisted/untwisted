"""
Description: Just send html back to the client.

Usage:
python app.py
"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, core, xmap

class Simple(object):
    def __init__(self, con):
        # Used to map a router to a handle.
        xmap(con, 'GET /', self.send_base)

    def send_base(self, con, header, fd, data, version):
        # The http response.
        response = Response()
        response.set_response('HTTP/1.1 200 OK')

        HTML = """ <html> 
                   <body>
                   <p> It is simple :P </p>
                   </body> </html>
               """

        response.add_data(HTML)

        # This function should be called just once.
        send_response(con, response)
    

if __name__ == '__main__':
    app = RapidServ('0.0.0.0', 5000, 60)

    app.add_handle(Simple)
    core.gear.mainloop()
    





