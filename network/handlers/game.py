# encoding: utf-8

from SZMUD.network.handler import Handler
from SZMUD.game import game


class GameHandler(Handler):

    def __init__(self, conn, account, char):
        Handler.__init__(self, conn)
        self.account = account
        self.character = char

    def Enter(self):
        self.character.AddLogic('BasicPlayerLogics', self.connection)
        game.ProcessEvent('EnterWorld', who=self.character)

    def Leave(self):
        game.ProcessEvent('LeaveWorld', who=self.character)

    def Handle(self, cmd):
        game.ExecuteCommand(self.character, cmd)
