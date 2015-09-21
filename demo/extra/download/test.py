from download import *

def main():
    with open('urls', 'r') as fd:
        urls = fd.read()
        urls = urls.split('\n')

    def done(task, data):
        raise Kill
    
    xmap(Download.task, COMPLETE, done)
    
    for addr in urls:
        Download(addr, '/')
    
    core.gear.mainloop()
main()

