# encoding: utf-8

import sockets
import connection

class ListeningManager:
    
    def __init__(self, conn_manager):
        self.conn_manager=  conn_manager
        self.pullset = sockets.SocketSet()
        self.listening_sockets = []

    def Stop(self):
        for socket in self.listening_sockets :
            socket.Close()
        
    def AddPort(self, port):
        """新建监听套接字"""
        ls = sockets.ListeningSocket()
        ls.Listen(port)
        ls.SetBlocking(False)
        
        self.listening_sockets.append(ls)
        self.pullset.AddSocket(ls)
        
    def Listen(self):
        """接受新连接"""
        rlist = self.pullset.Poll()
        # TODO(Prim): 忽略EOpertionWouldBlock的错误
        for ls in rlist:
            ds, remoteinfo = ls.accept()
            self.conn_manager.NewConnection(ds)
                

class ConnectionManager:
    
    def __init__(self, defaulthandler_class, protocol_class):
        self.defaulthandler_class = defaulthandler_class
        self.protocol_class = protocol_class
        self.connections = []
        self.pull_set = sockets.SocketSet()
    
    def Stop(self):
        for conn in self.connections:
            conn.CloseSocket()
    
    def NewConnection(self, ds):
        conn = connection.Connection(self.protocol_class, ds)
        conn.SetBlocking(False)
        handler = self.defaulthandler_class(conn)
        conn.AddHandler(handler)    
        self.connections.append(conn)
        self.pull_set.AddSocket(conn)
                        
    def Close(self, conn):
        self.pull_set.RemoveSocket(conn)
        conn.CloseSocket()
        self.connections.remove(conn)
        
    def _CloseConnections(self):
        for conn in self.connections:
            if conn.is_closed:
                self.Close(conn)
    
    def _Listen(self):
        rlist = self.pull_set.Poll()
        for conn_s in rlist:
            for conn in self.connections:
                if conn.socket == conn_s:
                    conn.ReceiveAndHandle()
            
    def _Send(self):
        for conn in self.connections:
            conn.SendBuffer()
    
    def Manage(self):
        self._Listen()
        self._Send()
        self._CloseConnections()
