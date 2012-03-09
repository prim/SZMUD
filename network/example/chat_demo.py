# encoding: utf-8

import sys

from string import punctuation as invalidchars

from telnet import *
from handler import Handler
from managers import ListeningManager, ConnectionManager


def is_valid_name(name):
    for char in name:
        if char in invalidchars:
            return False
    if not name.isalpha():
        return False
    if 3 > len(name) or len(name) > 26:
        return False
    return True

def get_username(conn):
    for user in all_users:
        if user.connection == conn:
            return  user.name
    raise Exception, 'Get a invalid connection!!!'

def remove_user(conn):
    global all_users
    all_users = [user for user in all_users if not user.connection == conn]

class User:

    def __init__(self, conn, name):
        self.connection = conn
        self.name = name


class LogonHandler(Handler):

    def __init__(self, conn):
        Handler.__init__(self, conn)

    def Enter(self):
        self.SendString(
                self.connection, 
                green + bold + 'Welcome To Simple Chat Room!' + newline + 
                'Please enter your username: ' + reset + bold + newline
            )

    def Leave(self):
        self.SendString(self.connection, 'Leave Logon Handler\n')

    def Handle(self, cmd):
        conn = self.connection
        name = cmd

        if not is_valid_name(name):
            self.SendString(
                    conn, 
                    'Sorry, that is an invalid username.' + newline +
                    'Please enter another username: ' + newline
                )

        if name in [user.name for user in all_users]:
            self.SendString(
                    conn,
                    'Sorry, that name is already in user.' + newline + 
                    'Please enter another username: ' + newline
                )
        all_users.append(User(conn, name))
        self.SendString(conn, 'Thank you for joining us, ' + name + newline)

        conn.RemoveHandler()
        conn.AddHandler(ChatHandler(conn))


class ChatHandler(Handler):

    def __init__(self, conn):
        Handler.__init__(self, conn)

    def _SendAll(self, string):
        for user in all_users:
            self.SendString(user.connection, string)

    def Enter(self):
        self._SendAll(
                blue + bold + get_username(self.connection) + ' has entered the room.' + newline
            )

    def Leave(self):
        self.SendString(self.connection, 'Leave Chat Handler\n')

    def Handle(self, cmd):
        conn = self.connection
        name = get_username(conn)

        if cmd.startswith('/who'):
            wholist = magenta + bold + 'Who is in the room: ' + newline
            wholist += ', '.join([user.name for user in all_users])
            wholist += newline
            self.SendString(conn, wholist)
                
        elif cmd.startswith('/quit'):
            self._SendAll(green + bold + '<' + name + '>' + reset + 'quit!' + newline)
            conn.Close()
            conn.RemoveHandler()
            remove_user(conn)

        else:
            self._SendAll(green + bold + '<' + name + '>' + reset + cmd + newline)

all_users = []

cm = ConnectionManager(LogonHandler, Telnet)
lm = ListeningManager(cm)
lm.AddPort(int(sys.argv[1]))

while True:
    lm.Listen()
    cm.Manage()
