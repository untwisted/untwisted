from untwisted.network import *
from untwisted.utils.stdio import Client, CONNECT, CONNECT_ERR, lose
import errno

def on_connect(con):
    print 'Connected to google.'
    

def on_connect_err(con, err):
    print "It couldn't connect, errcode ", errno.errorcode[err]
    lose(con)


con = Spin()
Client(con)
xmap(con, CONNECT, on_connect)
xmap(con, CONNECT_ERR, on_connect_err)

con.connect_ex(('www.google.com.br', 80))

core.gear.mainloop()




