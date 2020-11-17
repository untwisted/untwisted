from untwisted.expect import Expect
from subprocess import Popen, PIPE
from untwisted.event import LOAD, CLOSE
from untwisted.core import die
from untwisted import core

def on_load(stdout, data):
    print('Irc: ', data)

def on_close(expect):
    print('Closing..')
    die()

code = r"""
eee uu eee :foo\r\n
nick FuinhoMaroto\r\n
join #brazil\r\n
quit\r\n
"""
code = code.encode('utf8')

expect   = Expect('telnet', 'irc.undernet.org', '6667')
expect.send(code)
expect.add_map(LOAD, on_load)
expect.add_map(CLOSE, on_close)

core.gear.mainloop()

