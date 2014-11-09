from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.task import Task, COMPLETE

urls = ['www.google.com', 'www.yandex.ru', 'www.python.org']

class Accumulator(object):
    def __init__(self, spin):
        xmap(spin, LOAD, self.update)
        spin.accumulator = self
        self.data = ''

    def update(self, spin, data):
        self.data = self.data + data

def on_connect(con, url):
    Stdin(con)
    Stdout(con)
    Accumulator(con)

    con.dump('GET / HTTP/1.1\r\n')
    con.dump('Host: %s\r\n' % url)
    con.dump('Connection: TE, close\r\n')
    con.dump('User-Agent: UntwistedDownload/1.0\r\n\r\n')

def on_close(con, err, url):
    with open(url, 'w') as fd:
        fd.write(con.accumulator.data)

def done(task, data):
    raise Kill

task = Task(dict())
xmap(task, COMPLETE, done)

job = lambda data, event, args: True

for ind in urls:
    con = Spin()
    Client(con)
    con.connect_ex((ind, 80))
    xmap(con, CONNECT, on_connect, ind)
    xmap(con, CLOSE, lambda con, err: lose(con))
    xmap(con, CLOSE, on_close, ind)
    xmap(con, CONNECT_ERR, lambda con, err: lose(con))
    task.gather(con, (CLOSE, job),
                     (CONNECT_ERR, job))

core.gear.mainloop()

