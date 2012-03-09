# encoding: utf-8

# from string import letters, octdigits, punctuation
# 
# validchars = letters + octdigits + punctuation + ' '
# validchars = unicode(validchars)

class Telnet:

    def __init__(self):
        self.buffer = ''
    
    def Translate(self, conn, string):
        # TODO(Prim): ubuntu的telnet有bug，不能很好的处理中文，有后退符时会出错
        string = string.decode('utf-8')
        for c in string:
            # if c >= '\x30' and c < '\x7F':
            # if c in validchars:
            #     self.buffer += c
            # if c in invalidchars:
            #     continue
            # TODO(Prim): Ubuntu默认的telnet似乎在客户端就解决这些
            if c == u'\x08':
                self.buffer = self.buffer[:-1]
            elif c == u'\n' or c == u'\r':
                handler = conn.GetTopHandler()
                if self.buffer and handler:
                    handler.Handle(self.buffer)
                    self.buffer = ''
            else:
                self.buffer += c
        
    def SendString(self, conn, string):
        conn.BufferData(string)
    

reset = "\x1B[0m"
bold = "\x1B[1m"
dim = "\x1B[2m"
under = "\x1B[4m"
reverse = "\x1B[7m"
hide = "\x1B[8m"

clearscreen = "\x1B[2J"
clearline = "\x1B[2K"

black = "\x1B[30m"
red = "\x1B[31m"
green = "\x1B[32m"
yellow = "\x1B[33m"
blue = "\x1B[34m"
magenta = "\x1B[35m"
cyan = "\x1B[36m"
white = "\x1B[37m"

bblack = "\x1B[40m"
bred = "\x1B[41m"
bgreen = "\x1B[42m"
byellow = "\x1B[43m"
bblue = "\x1B[44m"
bmagenta = "\x1B[45m"
bcyan = "\x1B[46m"
bwhite = "\x1B[47m"

newline = "\r\n\x1B[0m"
