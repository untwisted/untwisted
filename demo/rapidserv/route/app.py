"""
Description: Just send html back to the client.

Usage:
python app.py
"""

from untwisted.plugins.rapidserv import RapidServ, send_response, Response, core
app = RapidServ('0.0.0.0', 80, 60)

@app.accept
def setup(con):
    pass

@app.route('/load')
def send_base(con, index, fd):
    response = Response()
    response.set_response('HTTP/1.1 200 OK')

    HTML = """ <html> 
               <body>
               <p> The index %s </p>
               </body> </html>
           """

    response.add_data(HTML % index)
    send_response(con, response)

if __name__ == '__main__':
    core.gear.mainloop()
    










