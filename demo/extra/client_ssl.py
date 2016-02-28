from untwisted.network import core, SSL, xmap
from untwisted.iostd import put
from untwisted.iossl import Client, Stdin, Stdout, CONNECT, CLOSE, LOAD
from socket import socket, AF_INET, SOCK_STREAM
import ssl

def on_connect(con):
    Stdin(con)
    Stdout(con)
    con.dump("GET / HTTP/1.0\r\nHost: www.google.com\r\n\r\n")
    xmap(con, LOAD, put)

def main():
    sock    = socket(AF_INET, SOCK_STREAM)
    context = ssl.create_default_context()
    con     = SSL(context.wrap_socket(sock, do_handshake_on_connect=False, server_hostname="www.python.org"))
    con.connect_ex(("www.python.org", 443))

    Client(con)
    xmap(con, CONNECT, on_connect)

if __name__ == '__main__':
    main()
    core.gear.mainloop()





