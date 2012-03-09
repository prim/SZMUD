# encoding: utf-8

from SZMUD.utils.jsdict import Action
from SZMUD.scripts.script import Script
from SZMUD.databases.database import CharacterDB


class UsageError(Exception):
    pass

class TargetError(Exception):
    pass

class Command(Script):

    def __init__(self, usage='', description=''):
        Script.__init__(self)
        self.usage = usage
        self.description = description

    def Execute(self, *args):
        try:
            self.Run(*args)
        except UsageError, message:
            self.me.React(Action('error', message=u'Usage: %s.\r\n' % message))
        except TargetError, message:
            self.me.React(Action('error', message=u'Candnot find: %s.\r\n' % message))
        except Exception, message:
            # TODO(Prim): log
            # import traceback; traceback.print_exc() 
            # self.me.React(Action('error', message=u'Unkown error: %s.\r\n' % message))
            raise

    def Run(self, *args):
        # args = (str1, str2, str3, ...)
        pass

    def ScriptInit(self):
        pass

    def UsageError(self):
        self.me.React(Action('Error', message=u'Usage: %s' % self.usaeg))

    def Announce(self, content):
        self.me.React(Action('Announce', content=content))
        self.me.React(Action('Announce', content=u'\r\n'))


