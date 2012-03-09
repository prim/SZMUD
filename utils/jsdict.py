# encoding: utf-8

class JsDict:

    def __init__(self, name, **kw):
        self.__dict__['type'] = name
        self.__dict__['dict'] = dict(**kw)

    def __iter__(self):
        for i in self.dict.keys():
            yield i

    def __nonzero__(self):
       return self.dict

    def __setattr__(self, name, value):
       self.dict[name] = value

    def __getattr__(self, name):
        return self.dict[name]

    def __delattr__(self, name):
        del self.dict[name]

    def __setitem__(self, name, value):
       self.dict[name] = value

    def __getitem__(self, name):
        return self.dict[name]

    def __delitem__(self, name):
        del self.dict[name]

    def __contain__(self, name):
        return name in self.dict

    def values(self):
        return self.dict.values()

    def items(self):
        return self.dict.items()


Action = JsDict
Condition = JsDict
Event = JsDict
