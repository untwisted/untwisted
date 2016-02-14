class Hold(object):
    def __init__(self, seq):
        self.seq              = seq
        self.mode, self.event = next(seq)
        self.mode.add_handle(self)

    def __call__(self, mode, event, args):
        if not self.event == event:
            return

        self.seq.send(args)
        try:
            mode, event = next(self.seq)
        except StopIteration:
            self.mode.del_handle(self)
        else:
            self.swap_dispatcher(event, self.mode, mode)

    def swap_dispatcher(self, event, mode_m, mode_n):
        self.event = event
        if mode_m == mode_n: return

        self.mode  = mode_n
        mode_m.del_handle(exec_iter)
        mode_n.add_handle(exec_iter)

def coroutine(handle):
    def start_iter(*args, **kwargs):
        seq  = handle(*args, **kwargs)
        hold = Hold(seq)
    return start_iter







