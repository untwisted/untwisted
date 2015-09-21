""" Name: irc.py
    Description: A small abstraction for irc protocol.

"""

from untwisted.network import spawn, xmap
from untwisted.utils.shrug import Shrug, FOUND
from re import match, compile

RFC_STR = "^(:(?P<prefix>[^ ]+) +)?(?P<command>[^ ]+)( *(?P<argument> .+))?"
RFC_REG = compile(RFC_STR)

class Irc(object):
    def __init__(self, spin):
        xmap(spin, FOUND, self.split)
    
    def split(self, con, data):
        try:
            reg = match(RFC_REG, data)
            prefix = reg.group('prefix')
            command = reg.group('command')
            argument = reg.group('argument')
        except:
            pass
        else:
            command = command.upper()
            spawn(con, command, prefix, argument)


