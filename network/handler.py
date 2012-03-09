# encoding: utf-8

class Handler:

    def __init__(self, conn):
        self.connection = conn
        self.protocol = conn.protocol
        
    def Handle(self, cmd):
        pass
        
    def Enter(self):
        pass
        
    def Leave(self):
        pass
        
    def SendString(self, conn, string):
        self.protocol.SendString(conn, string)
