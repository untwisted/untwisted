
# It imports basic untwisted objects.
# The irc protocol implementation.
from ircjob import xmap, zmap
import ircjob

def on_join(spin, *args):
    print 'on_join\n', args

def on_part(spin, *args):
    print 'on_part\n', args

def on_privmsg(spin, *args):
    print 'on_privmsg\n', args

def on_332(spin, *args):
    print 'on_332\n', args

def on_302(spin, *args):
    print 'on_302\n', args

def on_333(spin, *args):
    print 'on_333\n', args

def on_353(spin, *args):
    print 'on_353\n', args

def on_366(spin, *args):
    print 'on_366\n', args

def on_474(spin, *args):
    print 'on_474\n', args

def on_302(spin, *args):
    print 'on_302\n', args

def on_376(spin, *args):
    print 'on_376\n', args

def on_notice(spin, *args):
    print 'on_notice\n', args

def on_001(spin, *args):
    print 'on_001\n', args

def on_002(spin, *args):
    print 'on_002\n', args

def on_003(spin, *args):
    print 'on_003\n', args

def on_004(spin, *args):
    print 'on_004\n', args

if __name__ == '__main__':
    USER = 'uxirc uxirc uxirc :uxirc'
    NICK = 'uxirc'
    CMD = ('JOIN #&math',
           'PRIVMSG #&math :hello',
           'topic #calculus',
           'PART #&math :bye',
           'userhost %s' % NICK)
    
    # This call back will be called periodically.
    con = ircjob.main('irc.freenode.org', 6667, NICK, USER, CMD)

    xmap(con, 'JOIN', on_join)
    xmap(con, 'PART', on_part)
    xmap(con, '376', on_376)
    xmap(con, 'NOTICE', on_notice)
    xmap(con, 'PRIVMSG', on_privmsg)
    xmap(con, '332', on_332)
    xmap(con, '001', on_001)
    xmap(con, '001', on_002)
    xmap(con, '003', on_003)
    xmap(con, '004', on_004)
    xmap(con, '333', on_333)
    xmap(con, '353', on_353)
    xmap(con, '366', on_366)
    xmap(con, '474', on_474)
    xmap(con, '302', on_302)

    # it runs the reactor.
    ircjob.gear.mainloop()

