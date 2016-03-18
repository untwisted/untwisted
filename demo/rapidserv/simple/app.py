"""
"""

from untwisted.plugins.rapidserv import RapidServ, core, xmap

app = RapidServ(__file__)

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
    app.bind('0.0.0.0', 80, 60)
    core.gear.mainloop()










