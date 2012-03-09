# encoding: utf-8

import sys

from SZMUD.network.telnet import Telnet
from SZMUD.network.handlers import LoginHandler
from SZMUD.network.managers import ListeningManager, ConnectionManager

from SZMUD.game import game

# SZMUD main
port = int(sys.argv[1])
cm = ConnectionManager(LoginHandler, Telnet)
lm = ListeningManager(cm)
lm.AddPort(port)

game.LoadAll()

try:
    while game.is_running:
        lm.Listen()
        cm.Manage()
        game.ExecuteLoop()
except Exception, error:
    # TODO(Prim): log
    raise

game.SaveAll()

