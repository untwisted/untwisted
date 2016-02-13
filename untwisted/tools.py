def coroutine(handle):
    def start_iter(*args, **kwargs):
        seq = handle(*args, **kwargs)
        mode, event = next(seq)

        def exec_iter(m, e, a):
            if e != event: 
                return

            seq.send(a)
            m, e = next(seq)

            if e != event:
                event = e

            if m == mode: 
                return

            mode.del_handle(exec_iter)
            m.add_handle(exec_iter)
            mode = m
        mode.add_handle(exec_iter)
    return start_iter






