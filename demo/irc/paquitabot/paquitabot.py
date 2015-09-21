""" Name: paquitabot.py
    Description:  A simple plugable irc bot.
"""

from net import irc_connect, core
from spawncmd import *
from holdex import *
from untwisted.plugins.irc import send_msg
from untwisted.utils.shrug import logcon

con = irc_connect('irc.freenode.org', 6667, 'Fourier1', 'kaus keus kius :kous')
xmap(con, '376', lambda con, *args: con.dump('JOIN #&math\r\nJOIN #calculus\rn'))
xmap(con, '376', lambda con, *args: send_msg(con, 'nickserv', 'identify your_password'))
# Install our simple cmd event system.
SpawnCmd(con)
# It is a plugin class.
# You could write other plugins and install them here.
# This file is a kind of script bot.
HoldEx(con)
#DebugCmd(con)

# It is used to output everything 
# that comes from the irc server.
logcon(con)
#DoWhat(con)

core.gear.mainloop()

