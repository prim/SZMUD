# encoding: utf-8

from SZMUD.network.handler import Handler
from SZMUD.databases.database import CharacterDB, AccountDB, RoomDB, RegionDB

from game import GameHandler

class MenuHandler(Handler):

    def __init__(self, conn, account):
        Handler.__init__(self, conn)
        self.account = account

    def Enter(self):
        menu = [
                u'---------------------------------------------------------',
                u'BetterMUD v1.0 Main  Menu', 
                u'---------------------------------------------------------',
                u'0 - Quit', 
                u'1 - Enter The Game',
                u'2 - Create A New Character', 
                u'3 - Delete An Existing Character',
                u'4 - View Help',
                u'---------------------------------------------------------',
                u'Enter choice: ',
            ]
        self.SendString(self.connection, u'\r\n'.join(menu))

    def Handle(self, cmd):
        if cmd.isdigit():
            option = int(cmd)
            if option == 0:
                self.connection.Close()
            elif option == 1:
                self.connection.AddHandler(EnterHandler(self.connection, self.account))
            elif option == 2:
                if len(self.account.characters) >= self.account.allowedcharacters:
                    self.SendString(self.connection, u'Sorry, your are not allowed any more characters.\r\n')
                else:
                    self.connection.AddHandler(CreateHandler(self.connection, self.account))
            elif option == 3:
                self.connection.AddHandler(DeleteHandler(self.connection, self.account))
            elif option == 4:
                self.connection.AddHandler(HelpHandler(self.connection, self.account))
        else:
            self.SendString(self.connection, u'INVALID CHOICE!!!\r\nPlease Enter again: ')


class EnterHandler(Handler):

    def __init__(self, conn, account):
        Handler.__init__(self, conn)
        self.account = account

    def Enter(self):
        # choose order list
        self.characters = [None]
        string = [
                u'---------------------------------------------------------',
                u'Your Characters:', 
                u'---------------------------------------------------------',
                u'0 - Go Back', 
            ]
        index = 1
        for character in self.account.characters:
            string.append(str(index)+' - '+character.name)
            self.characters.append(character)
            index += 1
        string.append(u'---------------------------------------------------------')
        string.append(u'Enter choice: ')
        self.SendString(self.connection, u'\r\n'.join(string))

    def Handle(self, cmd):
        if cmd.isdigit():
            option = int(cmd)
            if option == 0:
                self.connection.RemoveHandler()
            elif option > len(self.account.characters):
                self.SendString(self.connection, u'INVALID CHOICE!!!\r\nPlease enter a new choice: ')
            else:
                character = self.characters[option]
                self.connection.SwitchHandler(GameHandler(self.connection, self.account, character))

        else:
            self.SendString(self.connection, u'INVALID CHOICE!!!\r\nPlease enter a number: ')


class CreateHandler(Handler):

    def __init__(self, conn, account):
        Handler.__init__(self, conn)
        self.account = account
        self.character = None

    def Enter(self):
        races = [
                u'---------------------------------------------------------',
                u'Please Choose a Race For Your Character:', 
                u'---------------------------------------------------------',
                u'0 - Go Back', 
                u'1 - 半人马酋长',
                u'2 - 恶魔巫师', 
                u'---------------------------------------------------------',
                u'Enter choice: ',
            ]
        self.SendString(self.connection, u'\r\n'.join(races))

    def Handle(self, cmd):
        if self.character:
            if not AccountDB.IsAcceptName(cmd):
                self.SendString(self.connection, u'Sorry, the account name is unacceptible.\r\nPlease enter another name: ')

            elif CharacterDB.FindName(cmd):
                self.SendString(self.connection, u'Sorry, the account name %s has already been taken.\r\nPlease enter another name: ' % cmd)
            else:
                self.character.name = cmd
                self.connection.RemoveHandler()

        else:
            if cmd.isdigit():
                option = int(cmd)
                if option == 0:
                    self.connection.RemoveHandler()
                else:

                    if len(self.account.characters) >= self.account.allowedcharacters:
                        self.SendString(self.connection, u'Sorry, your are not allowed any more characters.\r\n')
                    else:
                        self.character = CharacterDB.Generate(option)
                        self.character.account = self.account.id
                        self.account.AddCharacter(self.character)
                        self.SetupCommands(self.character, self.account)
                        self.SendString(self.connection, u'Please your desired name: ')
            else:
                self.SendString(self.connection, u'INVALID CHOICE!!!\r\nPlease Enter again: ')

    # TODO(Prim): 
    def SetupCommands(self, character, account):
        l = account.accesslevel
        if l >= 0:
            character.AddCommand('Go')

            character.AddCommand('Items')
            character.AddCommand('Commands')
            character.AddCommand('Say')
            character.AddCommand('Look')
            character.AddCommand('Quit')
            character.AddCommand('Quiet')

            character.AddCommand('Get')
            character.AddCommand('Drop')
            character.AddCommand('Give')
            character.AddCommand('Self')

            character.AddCommand('AddF')
            character.AddCommand('DelF')
            character.AddCommand('FS')

        # if l >= 1:
            character.AddCommand('Shutdown')
            # character.AddCommand('LoadDatabase')
            character.AddCommand('SaveDatabase')

            # character.AddCommand('Kick')

            # character.AddCommand('Python')


            # character.AddCommand('AddCommand')
            # character.AddCommand('DelCommand')
            # character.AddCommand('AddPlayerLogic')
            # character.AddCommand('DelPlayerLogic')

            # character.AddCommand('SpawnItem')
            # character.AddCommand('SpawnCharacter')

            # character.AddCommand('DestoryItem')
            # character.AddCommand('DestoryCharacter')


        if l >= 2:
            pass
        if l >= 3:
            pass
        if l >= 4:
            pass
        
        character.room = RoomDB[1]
        character.region = RegionDB[1]


# TODO(Prim): 
class DeleteHandler(Handler):
    pass


# TODO(Prim): 
class HelpHandler(Handler):
    pass


