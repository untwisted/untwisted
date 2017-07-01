from untwisted.dispatcher import Dispatcher

xmap  = Dispatcher.add_map
zmap  = Dispatcher.del_map
spawn = Dispatcher.drive

def once(dispatcher, event, handle, *args):
    """
    Used to do a mapping like event -> handle
    but handle is called just once upon event.
    """

    def shell(dispatcher, *args):
        try:
            handle(dispatcher, *args)
        except Exception as e:
            raise e
        finally:
            dispatcher.del_map(event, shell)
    dispatcher.add_map(event, shell, *args)


