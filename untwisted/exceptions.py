class Stop(Exception):
    """
    This exception is used to avoid remaining handles being
    processed for a given event.

    from untwisted.dispatcher import Dispatcher, Stop
    
    def handle0(dispatcher):
        raise Stop
    
    def handle1(dispatcher):
        print 'it will not be processed!'
    
    dispatcher = Dispatcher()
    dispatcher.add_map('alpha', handle0)
    dispatcher.add_map('alpha', handle1)
    dispatcher.drive('alpha')
    """
    pass

class Erase(Exception):
    """
    When this exception is thrown from a handle it avoids such a handle
    being processed again upon its event.

    from untwisted.dispatcher import Dispatcher, Erase
    
    def handle(dispatcher):
        print 'It will be called just once!'
        raise Erase
    
    dispatcher = Dispatcher()
    dispatcher.add_map('alpha', handle)
    dispatcher.drive('alpha')
    dispatcher.drive('alpha')
    """

    pass

