"""
"""

from untwisted.plugins.requests import HttpResponseHandle, post
from untwisted.network import Spin, xmap, core, die
import argparse

def on_done(spin, response):
    print 'URL:%s' % response.headers['location']
    die()

if __name__ == '__main__':
    parser= argparse.ArgumentParser()
    parser.add_argument('-f', '--filename',  default='0.0.0.0', help='filename')
    parser.add_argument('-t', '--type',  default='Plain Text', 
                                help='Type should be Python, Haskell, etc..')
    parser.add_argument('-r', '--run',  action='store_true', help='run')
    args = parser.parse_args()

    fd   = open(args.filename, 'r')
    code = fd.read()
    fd.close()

    payload = {
                    'code':code,
                    'lang':' '.join(map(lambda ind: ind.capitalize(), 
                                        args.type.split(' '))),
                    'submit':'Submit',
                    'run': args.run
              }
    
    con = post('codepad.org', 80, '/', payload)
    xmap(con, HttpResponseHandle.HTTP_RESPONSE, on_done)
    core.gear.mainloop()






