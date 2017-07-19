from __future__ import print_function
from untwisted.expect import Expect, LOAD, CLOSE
from untwisted.network import core, xmap, die

def handle(expect, data):
    print(data)

def on_close(expect):
    print('Closing..')
    die()

expect = Expect('python', '-i', '-u')

expect.send(b'print("hello world");quit();\n\n')

xmap(expect, LOAD, handle)
xmap(expect, CLOSE, on_close)

core.gear.mainloop()






