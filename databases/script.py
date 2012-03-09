# encoding: utf-8

import os
import sys


class ScriptManager:

    def __init__(self, directory):
        self.modules = {}
        self.directory = directory
        sys.path.append(os.path.realpath(directory))

    def Load(self):
        for modname in open(self.directory + 'manifest'):
            modname = modname.strip()
            if modname:
                self.modules[modname] = __import__(modname)

    # def ReLoad(self):
    #     pass

    def AddModule(self, modulename):
        self.modules[modulename] = __import__(modulename)

        # TODO:
        with open(self.directory+'mainifest') as f:
            pass

    def SpawnNew(self, modulename, classname):
        return getattr(self.modules[modulename], classname)()

    def Generate(self, classname, entity):
        for modname, mod in self.modules.items():
            # attrs = {}
            # for attr in dir(mod):
            #     attrs[attr.lower()] = attr
            # if classname.lower() in attrs:
            #     return getattr(self.modules[modname], attrs[classname])('usage', 'description')
            if hasattr(mod, classname):
                instance =  getattr(self.modules[modname], classname)()
                # TODO(Prim): 
                instance.me = entity
                instance.ScriptInit()
                return instance
        raise Exception, 'Try generate a invalid script: %s.' % classname


LogicDB = ScriptManager('scripts/logics/')
CommandDB = ScriptManager('scripts/commands/')
