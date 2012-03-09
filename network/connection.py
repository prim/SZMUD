# encoding: utf-8

import sockets

class Connection(sockets.DataSocket):
    
    def __init__(self, protocol_class, socket = None):
        if socket:
            sockets.DataSocket.__init__(self, socket)

        self.sendbuffer = ''
        self.recvbuffer = ''
        self.handlerstack = []
        self.protocol = protocol_class()

        # TODO(Prim): 
        # self.datarate = 0
        # self.last_datarate = 0
        # self.last_receive_tiem = 0
        # self.last_send_time = 0
        # self.creatie_time = 0
        # self.is_check_send_time = False
        self.is_closed = False
    
    def BufferData(self, data):
        self.sendbuffer += data
    
    def SendBuffer(self):
        if len(self.sendbuffer):
            n = self.Send(self.sendbuffer)
            self.sendbuffer = self.sendbuffer[n:]
    
    def ReceiveAndHandle(self):
        # TODO(Prim): 
        self.recvbuffer = sockets.DataSocket.Receive(self, 1024)
        self.protocol.Translate(self, self.recvbuffer)
        
    def Close(self):
        self.is_closed = True
    
    def CloseSocket(self):
        sockets.DataSocket.Close(self)
        self.ClearHandlers()
    
    # TODO(Prim): 分辨各个方法的具体作用
    def GetTopHandler(self):
        return self.handlerstack[-1] if self.handlerstack else None

    def SwitchHandler(self, handler):
        """del current handler, add a new one"""
        if self.GetTopHandler():
            self.GetTopHandler().Leave()
            del self.handlerstack[-1]
        
        self.handlerstack.append(handler)
        handler.Enter()
        
    def AddHandler(self, handler):
        # NOTE: 并不删除当前的处理器
        if self.GetTopHandler():
            self.GetTopHandler().Leave()
        self.handlerstack.append(handler)
        handler.Enter()

    def ClearHandlers(self):
        if self.GetTopHandler():
            self.GetTopHandler().Leave()
        while self.GetTopHandler():
            del self.handlerstack[-1]
    
    def RemoveHandler(self):
        self.GetTopHandler().Leave()
        del self.handlerstack[-1]
        
        if self.GetTopHandler():
            self.GetTopHandler().Enter()
