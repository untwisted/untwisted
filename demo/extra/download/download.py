from untwisted.network import *
from untwisted.utils.stdio import *
from untwisted.task import Task, COMPLETE
from untwisted.utils.accumulator import *
from re import findall, compile


HTTP_HEADER = 'GET %s HTTP/1.1\r\nHost: %s\r\nConnection: TE, close\r\nUser-Agent: UntwistedDownload/1.0\r\n\r\n'
STR_HEADER = "(?P<name>.*?): (?P<value>.*?)\r\n"
REG_HEADER = compile(STR_HEADER)

class Download(object):
    task = Task(dict())
    job = lambda self, data, event, args: True

    def __init__(self, addr, rsc):
        self.addr = addr
        self.rsc = rsc

        con = Spin()
        Client(con)
        con.connect_ex((addr, 80))

        xmap(con, CONNECT, self.on_connect)
        xmap(con, CLOSE, lambda con, err: lose(con))
        # The event CLOSE is binded to self.on_close before
        # we call self.task.gather on con, it needs to be so
        # otherwise it might happen of the last Download
        # instance to finish spawn CLOSE and the COMPLETE
        # event be spawned too early. It needs first 
        # check whether there is a Location http key in the
        # headers.
        xmap(con, CLOSE, self.on_close)
        
        xmap(con, CONNECT_ERR, lambda con, err: lose(con))
        
        self.task.gather(con, (CLOSE, self.job),
                         (CONNECT_ERR, self.job))

    def on_connect(self, con):
        Stdin(con)
        Stdout(con)
        Accumulator(con)
        
        con.dump(HTTP_HEADER % (self.rsc, self.addr))
    
    def on_close(self, con, err):
        data = con.accumulator.data

        try:
        # It might happen of the webserver
        # sending only the http header then splitting up 
        # will raise an exception.
            header, data = data.split('\r\n\r\n', 1)
        # I lower all letters so i don't have to worry
        # when indexing location in the dict.
            header = header.lower()
        # It builds the http header.
            header = findall(REG_HEADER, header)
            header = dict(header)
        # If it occurs of the document having moved
        # to other place then we follow the link.
            addr = header['location']
            _, addr = addr.split('//')
            addr, rsc = addr.split('/', 1)
        # After properly extracting the new documment
        # address we download it.
            Download(addr, rsc)
        except:
        # If some exception occured all what we want is saving
        # what we have in hands.
            with open(self.addr, 'w') as fd:
                fd.write(data)
        


def main():
    urls = [('www.google.com', '/'), ('www.yandex.ru', '/'), ('www.python.org', '/')]

    def done(task, data):
        raise Kill
    
    xmap(Download.task, COMPLETE, done)
    
    for addr, rsc in urls:
        Download(addr, rsc)
    
    core.gear.mainloop()

if __name__ == '__main__':
    main()



