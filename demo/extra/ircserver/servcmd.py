from untwisted.network import *
from untwisted.utils.shrug import FOUND

import re

CMD_STR = '(?P<cmd>.+?) (?P<argument>.+)'
CMD_REG = re.compile(CMD_STR)
ARGUMENT_STR = "[^: ]+|:.+"
ARGUMENT_REG = re.compile(ARGUMENT_STR)

empty = lambda data: data if data else ''

def install(spin):
    spin.link(FOUND, spliter)

def spliter(spin, data):
    field = re.match(CMD_REG, data)

    if not field:
        return

    cmd = field.group('cmd')
    argument = field.group('argument')

    spawn(spin, cmd, *extract_argument(argument))


def extract_argument(argument):
    return tuple(re.findall(ARGUMENT_REG, empty(argument)))

