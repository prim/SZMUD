# encoding: utf-8

from SZMUD.scripts.script import Script


class Logic(Script):

    def __init__(self):
        Script.__init__(self)

    def React(self, action):
        return True

    def ScriptInit(self):
        pass

