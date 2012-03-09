# encoding: utf-8

import socket
import select

# TODO(Prim): python中文件描述字被抽象为file鸭子类型 

class Socket:
    """设置本地的信息，提供几个常用方法"""

    def __init__(self, socket):
        # TODO(Prim): C++继承时构造函数调用还要再去弄明白
        # 设置本地信息
        self.socket = socket
        if socket:
            self.localinfo = {
                    'ip':self.socket.getsockname()[0],
                    'port':self.socket.getsockname()[1],
                }
        self.is_blocking = True

    def Close(self):
        self.socket.close()
        self.socket = None
        
    def SetBlocking(self, will_block):
        if will_block:
            self.socket.setblocking(True)
        else:
            self.socket.setblocking(False)
        self.is_blocking = will_block


class ListeningSocket(Socket):
    
    def __init__(self):
        self.is_listening = False
        
    def Listen(self, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind(('', port))
        self.socket.listen(128)
        self.localinfo = {
                'ip':self.socket.getsockname()[0],
                'port':self.socket.getsockname()[1],
            }
                
        self.is_listening = True
        
    def Accept(self):
        datasocket, remoteinfo = self.socket.accept()
        return DataSocket(datasocket)

    def Close(self):
        Socket.Close(self)
        self.is_listening = True


class DataSocket(Socket):

    def __init__(self, socket = None):
        Socket.__init__(self, socket)
        self.is_connected = False
        if socket:
            self.remoteinfo = {
                    'ip':self.socket.getpeername()[0],
                    'port':self.socket.getpeername()[1],
                }
            self.is_connected = True
        
    def Close(self):
        if self.is_connected:
            # TODO(Prim): 
            self.socket.shutdown(socket.SHUT_RDWR)
        self.is_connected = False
        Socket.Close(self)
    
    def Connect(self, addr, port):
        if self.is_connected:
            raise Exception, 'This socket is already connected'
        if not self.socket:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((addr, port))
        self.is_connected = True
        self.localinfo = {
                'ip':self.socket.getsockname()[0],
                'port':self.socket.getsockname()[1],
            }
        self.remoteinfo = {
                'ip':self.socket.getpeername()[0],
                'port':self.socket.getpeername()[1],
            }
        
    def Send(self, buf):
        if self.is_connected:
            if type(buf) == unicode:
                return self.socket.send(buf.encode('utf-8'))
            elif type(buf) == str:
                return self.socket.send(buf)
            else:
                # TODO(Prim): 
                raise Exception, 'xxxx encoding '
    
    def Receive(self, size):
        if self.is_connected:
            return self.socket.recv(size)


class SocketSet:

    def __init__(self):
        self.sockets = [] # for class Sockets
        self.activitys = [] # for build-in socket
        
    def AddSocket(self, socket):
        self.sockets.append(socket)
    
    def RemoveSocket(self, socket):
        self.sockets.remove(socket)
    
    def Poll(self, time=1):
        poll_set = [i.socket for i in self.sockets]
        if poll_set:
            self.activitys, _, __ = select.select(poll_set, [], [], time)
        return self.activitys if self.activitys else []

