class ServerSSL(Server):
    def __init__(self, spin):
        xmap(spin, READ, self.update)

    def update(self, spin):
        pass


