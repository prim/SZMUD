# encoding: utf-8

import sys

from telnet import Telnet
from handler import Handler
from managers import ListeningManager, ConnectionManager

# from _handlers import LogonHandler

class EchoHandler(Handler):

    def __init__(self, conn):
        Handler.__init__(self, conn)

    def Enter(self):
        self.SendString(self.connection, 'Enter Echo Handler\n')

    def Leave(self):
        self.SendString(self.connection, 'Leave Echo Handler\n')

    def Handle(self, cmd):
        if cmd != 'quit':
            self.SendString(self.connection, 'Echo Command: %s\n' % cmd)
            print 'Recv cmd: %s' % cmd
        else:
            self.SendString(self.connection, 'Good Bye!\n')
            self.connection.Close()

# cm = ConnectionManager(LogonHandler, Telnet)
cm = ConnectionManager(EchoHandler, Telnet)
lm = ListeningManager(cm)
lm.AddPort(int(sys.argv[1]))

while True:
    lm.Listen()
    cm.Manage()
