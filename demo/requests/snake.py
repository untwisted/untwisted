from untwisted.plugins.requests import get, HttpResponseHandle
from untwisted.network import xmap, core

def on_done(con, response):
    print response.headers
    print response.code
    print response.version
    print response.reason 
    print response.fd.read()

if __name__ == '__main__':
    urls = ['www.bol.uol.com.br', 'www.google.com']
    
    for ind in urls:
        con = get(ind, 80, '/')
        xmap(con, HttpResponseHandle.HTTP_RESPONSE, on_done)
    core.gear.mainloop()





