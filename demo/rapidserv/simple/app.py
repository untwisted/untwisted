"""
"""

from untwisted.plugins.rapidserv import RapidServ, xmap
app = RapidServ()

@app.accept
class Simple(object):
    def __init__(self, con):
        xmap(con, 'GET /', self.send_base)

    def send_base(self, con, request):
        HTML = """ <html> 
                   <body>
                   <p> It is simple :P </p>
                   </body> </html>
               """

        con.add_data(HTML)
        con.done()

if __name__ == '__main__':
    app.run('0.0.0.0', 80, 60)










