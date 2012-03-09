# -*- coding: utf-8 -*-

class LoadStream:

    def __init__(self, filename):
        self.buf = []
        with open(filename) as file:
            for line in file:
                for word in line.split():
                    self.buf.append(word.decode('utf-8'))
        self.buf.reverse()

    def LoadInt(self):
        return int(self.buf.pop())
    
    def LoadString(self):
        string = self.buf.pop()
        if '_' in string:
            return string.replace('_', ' ')
        return string

    def IsEnd(self):
        return self.buf

    li = LoadInt
    ls = LoadString
    ll = LoadString
    eof = IsEnd


class SaveStream:

    def __init__(self, filename):
        self.file = open(filename, 'w')
    
    def SaveInt(self, i):
        self.file.write(str(i))
        return self
    
    def SaveString(self, string):
        self.file.write(string.encode('utf-8'))
        return self
    
    def SaveLine(self, line):
        if ' ' in line:
            line = line.replace(' ', '_')
        self.file.write(line.encode('utf-8'))
        return self
    
    def SaveEndl(self):
        self.file.write('\n')
        return self

    si = SaveInt
    ss = SaveString
    sl = SaveLine
    endl = SaveEndl
