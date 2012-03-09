# encoding: utf-8


class Script:

    def __init__(self):
        self.name = self.__class__.__name__

    def Load(self, stream):
        stream.ls(); string = stream.ls() # name, [DATA]
        data = []
        while string != '[/DATA]':
            data.append(stream.ls())
        self.LoadScript(data)

    def Save(self, stream):
        stream.ss("[DATA]").endl() 
        self.SaveScript(stream)
        stream.ss("[/DATA]").endl() 

    def LoadScript(self, data):
        pass

    def SaveScript(self, stream):
        pass

    def CanSave(self):
        return True

    def ScriptInit(self):
        pass
