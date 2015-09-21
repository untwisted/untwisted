from untwisted.network import xmap, hold
from untwisted.plugins.irc import send_msg

class HoldEx(object):
    """ Protocol class a.k.a plugin.
        Description:This class is used to demonstrate the usage of yield hold(spin, event)
        feature with uxirc implementation.

        Example:

        Fourier1 has joined #&math
        <blackdawn>which is your nick?
        <Fourier1>blackdawn My nick is Fourier1


        It prints on the screen.

        <untwisted.network.Spin object at 0x85bcc6c> holmes.freenode.net Fourier1 No nickname given

    """

    def __init__(self, spin):
        xmap(spin, 'which is your nick?', self.get_nick)

    def get_nick(self, spin, nick, user, host, target, msg):
        # We aim to receive a '431' reply from the server.
        # Consequently we can obtain the nick.
        send_cmd(spin, 'NICK')

        # It waits for the event to happen once it happens
        # the untwisted system of events chains this iterator
        # and starts where it stopped.
        event, args = yield hold(spin, '431')

        # Unpacks the arguments.
        source, prefix, mynick, cmd_msg = args

        # Tells which nick it uses.
        send_msg(spin, target, '%s My nick is %s' % (nick, mynick)) 

        # This prints all what '431' carries.
        print source, prefix, mynick, cmd_msg

        # As you might notice source is the 'spin' instance. 
        # It means it is where the event occured. You could have
        # other Spin instance if you had used hold(other_spin, event)
        # event consequently will be '431' but it could be different
        # if you had passed '431', '432' etc. It would mean
        # you are expecting one of those events any of them
        # is a sufficient condition to chain this iterator.




