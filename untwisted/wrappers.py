xmap  = lambda dispatcher, *args: dispatcher.add_map(*args)
zmap  = lambda dispatcher, *args: dispatcher.del_map(*args)
spawn = lambda dispatcher, *args: dispatcher.drive(*args)

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

