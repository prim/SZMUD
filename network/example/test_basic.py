# encoding: utf-8

from sockets import ListeningSocket

lsock = ListeningSocket()
import pdb; pdb.set_trace() 
lsock.Listen(5098)
dsock = lsock.Accept()
dsock.Send('Hello!\r\n')

while True:
    string = dsock.Receive(128)
    print 'Receive string: %s, From %s' % (string.strip(), dsock.remoteinfo['ip'])
    dsock.Send(string)
