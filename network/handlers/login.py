# encoding: utf-8

from SZMUD.network.handler import Handler
from SZMUD.network.handlers.menu import MenuHandler
from SZMUD.entities.entities import accesslevel
from SZMUD.databases.database import AccountDB


ENTER_NAME = 0 
ENTER_NEW_NAME = 1 
ENTER_NEW_PASS = 2
ENTER_PASS = 3 
ENTER_DEAD = 4 


class LoginHandler(Handler):

    def __init__(self, conn):
        Handler.__init__(self, conn)
        self.state = ENTER_NAME
        self.errors = 0
        self.account = None

    def Enter(self):
        with open('data/login/welcome.data') as file:
            string = file.read()
            self.SendString(self.connection, string.decode('utf-8'))

    def Handle(self, cmd):
        if self.errors == 5:
            self.SendString(self.connection, u'Too many incorrect reponse, closing connection...\r\n')
            self.connection.Close()

        elif self.state == ENTER_NAME:
            # 新用户进入注册
            if cmd == 'new': 
                with open('data/login/newaccount.data') as file:
                    string = file.read()
                    self.state = ENTER_NEW_NAME
                    self.SendString(self.connection, string.decode('utf-8'))
    
            # 旧用户登录
            else:
                account = AccountDB.FindName(cmd)
                if account:
                    self.state = ENTER_PASS
                    self.account = account
                    if account.is_banned:
                        self.SendString(self.connection, u'SORRY! Your ar BANNED!\r\n')
                        self.connection.Close()
                        self.state = ENTER_DEAD
                    else:
                        self.SendString(self.connection, u'Welcome! Please enter your password: \r\n')
                else:
                    self.errors += 1
                    self.SendString(self.connection, u'Sorry, the account dose not exist.\r\nPlease enter your name, or "name" if you are new: ')

        elif self.state == ENTER_PASS:
            if cmd == self.account.password:
                self.SendString(self.connection, u'Thank you! You are now entering the world...\r\n')
                self.GotoMenu()
            else:
                self.errors += 1
                self.SendString(self.connection, u'INVALID PASSWORD!!!\r\nPlease enter you password: ')

        elif self.state == ENTER_NEW_NAME:
            account = AccountDB.FindName(cmd)
            if account:
                self.errors += 1
                self.SendString(self.connection, u'Sorry, the account name %s has already been taken.\r\nPlease enter another name: ' % cmd)
            else:
                if AccountDB.IsAcceptName(cmd):
                    self.name = cmd
                    self.state = ENTER_NEW_PASS
                    self.SendString(self.connection, u'Please enter your desired password: ')
                else:
                    self.SendString(self.connection, u'Sorry, the account name is unacceptible.\r\nPlease enter another name: ')


        elif self.state == ENTER_NEW_PASS:
            if len(cmd) > 3 and len(cmd) < 17:
                self.account = AccountDB.CreateNewAccount(self.name, cmd)
                if not AccountDB.Size():
                    self.account.accesslevel = accesslevel['Admin']
                self.SendString(self.connection, u'Thank you! You are now entering the world...\r\n')
                self.GotoMenu()
            else:
                self.errors += 1
                self.SendString(self.connection, u'The password\'s length should > 5 and < 17.\r\n')

    def GotoMenu(self):
        self.connection.RemoveHandler()
        self.connection.AddHandler(MenuHandler(self.connection, self.account))
