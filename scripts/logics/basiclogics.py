# encoding: utf-8

from SZMUD.scripts.logics.logic import Logic


class BasicPlayerLogics(Logic):

    def __init__(self):
        Logic.__init__(self)

    def CanSave(self):
        return False

    def React(self, action):

        # TODO(Prim): 确定收到的编码
        if action.type == 'Error':
            self.SendString(u'%s\r\n' % action.message)
        elif action.type in ['See', 'Announce']:
            self.SendString(u'%s\r\n' % action.content)
        elif action.type == 'Say':
            self.SendString(u'%s 说: %s\r\n' % (action.who.name, action.content))
        elif action.type == 'News':
            with open('data/login/news.data') as news:
                self.SendString(news.read().decode('utf-8'))
        # elif action.type == 'Bye':
        #     with open('data/login/news.data') as news:
        #         self.SendString(news.read().decode('utf-8'))
       
        #------------------------------------------------------------------------------ 

        elif action.type == 'Quit':
            self.connection.RemoveHandler()

        elif action.type == 'SeeRoom':
            self._SeeRoom(self.me.room)
       
        #------------------------------------------------------------------------------ 

        # elif action.type == 'SpawnItem':
        #     self.SendString(u'%s enters the world.\r\n' % action.who.name)
        # elif action.type == 'SpawnCharacter':
        #     self.SendString(u'%s leaves the world.\r\n' % action.who.name)
        # elif action.type == 'DestoryItem':
        #     self.SendString(u'%s enters this region.\r\n' % action.who.name)
        # elif action.type == 'DestoryCHaracter':
        #     self.SendString(u'%s leaves this region.\r\n' % action.who.name)

        #------------------------------------------------------------------------------ 

        elif action.type == 'EnterWorld':
            self.SendString(u'%s进入了游戏。\r\n' % action.who.name)
        elif action.type == 'LeaveWorld':
            self.SendString(u'%s离开了游戏。\r\n' % action.who.name)
        elif action.type == 'EnterRegion':
            self.SendString(u'%s来到了%s。\r\n' % (action.who.name, action.who.region.name))
        elif action.type == 'LeaveRegion':
            self.SendString(u'%s离开了%s。\r\n' % (action.who.name, action.who.region.name))
        elif action.type == 'EnterRoom':
            self.EnterRoom(action.who, action.portal)
        elif action.type == 'LeaveRoom':
            self.LeaveRoom(action.who, action.portal)

        #------------------------------------------------------------------------------ 

        # elif action.type == 'EnterWorld':
        #     self.SendString(u'%s enters the world.\r\n' % action.who.name)
        #     
        # elif action.type == 'LeaveWorld':
        #     self.SendString(u'%s leaves the world.\r\n' % action.who.name)
        #     
        # elif action.type == 'EnterRegion':
        #     self.SendString(u'%s enters this region.\r\n' % action.who.name)
        #     
        # elif action.type == 'LeaveRegion':
        #     self.SendString(u'%s leaves this region.\r\n' % action.who.name)
       
        #------------------------------------------------------------------------------ 

        # TODO(Prim): 
        elif action.type == 'GiveItem':
            self.SendString(u'%s enters the world.\r\n' % action.who.name)
            
        elif action.type == 'DropItem':
            self.DropItem(action)
            
        elif action.type == 'GetItem':
            self.GetItem(action)
            
        # elif action.type == 'Die':
        #     self.SendString(u'%s leaves this region.\r\n' % action.who.name)

        # elif action.type == 'Whisper':
        #     self.SendString(u'%s leaves this region.\r\n' % action.who.name)

        # elif action.type == 'Chat':
        #     self.SendString(u'%s leaves this region.\r\n' % action.who.name)

        # elif action.type == 'Vision':
        #     self.SendString(u'%s leaves this region.\r\n' % action.who.name)


        return True

    def _SeeRoomName(self, room):
        self.SendString(room.name)
        self.SendString(u'\r\n')

    def _SeeRoomDesc(self, room):
        self.SendString(room.description)
        self.SendString(u'\r\n---------------------------------------------------------\r\n')

    def _SeeRoomExits(self, room):
        if len(room.portals) == 0:
            return 
        string = [u'出口: ']
        for ps in room.portals:
            for p in ps.portals:
                if p.startroom == room.id:
                    string.append(u'%s - %s' % (p.directionname, ps.name))
        self.SendString(u'\r\n'.join(string))
        self.SendString(u'\r\n---------------------------------------------------------\r\n')

    def _SeeRoomCharacters(self, room):
        if len(room.characters) == 0:
            return 
        # TODO(Prim): 调整格式
        string = [u'人物: ']
        for c in room.characters:
            string.append(c.name)
        self.SendString(u'\r\n'.join(string))
        self.SendString(u'\r\n---------------------------------------------------------\r\n')

    def _SeeRoomItems(self, room):
        if len(room.items) == 0:
            return 
        # TODO(Prim): 调整格式
        string = [u'物品: ']
        for i in room.items:
            string.append(i.Name())
        self.SendString(u'\r\n'.join(string))
        self.SendString(u'\r\n---------------------------------------------------------\r\n')

    def _SeeRoom(self, room):
        c = self.me
        self._SeeRoomName(room)
        if c.is_verbose:
            self._SeeRoomDesc(room)
        self._SeeRoomExits(room)
        self._SeeRoomCharacters(room)
        self._SeeRoomItems(room)

    def EnterRoom(self, character, portal=None):
        # 本人进入房间
        if character == self.me:
            self._SeeRoom(self.me.room)

        # 其他人进入房间
        elif portal == None:
            self.SendString(u'%s突然间出现了。\r\n' % character.name)

        else:
            self.SendString(u'%s从%s进来了。\r\n' % (character.name, portal.name))

    def LeaveRoom(self, character, portal=None):

        # 本人离开房间
        if character == self.me:
            if not portal:
                pass
                # self.SendString(u'你离开了\r\n')
            else:
                self.SendString(u'你进入了%s。\r\n' % portal.name)
        # 其他人离开房间
        elif not portal:
            self.SendString(u'%s突然间消失了。\r\n' % character.name)

        else:
            self.SendString(u'%s进入了%s。\r\n' % (character.name, portal.name))

    def Died(self, character):
        if character == self.me:
            self.SendString(u'YOU HAVE DIED!!!\r\n')
        else:
            self.SendString(u'%s HAS DIED!!!\r\n' % character.name)

    # TODO(Prim): 
    def GetItem(self, action):
        c = action.who
        i = action.item
        if c == self.me:
            string = u'你捡起了%s。' % i.Name()
        else:
            string = u'%s建起了%s。' % (c.name, i.Name())
        self.SendString(string)

    def DropItem(self, action):
        c = action.who
        i = action.item
        if c == self.me:
            string = u'You drop %s' % i.Name()
        else:
            string = u'%s drops ' % (c.name, i.name())
        self.SendString(string)

    def GiveItem(self, character, item):
        pass

    # TODO(Prim): 调整网络部分的设计，有点DT了
    def SendString(self, string):
        self.connection.protocol.SendString(self.connection, string)


class SuperGlue(Logic):
    pass


class CantReceiveItems(Logic):
    pass


class Encumbrance(Logic):
    pass


class Armaments(Logic):
    pass


class Merchant(Logic):
    pass


class Pies(Logic):
    pass


class Glarepie(Logic):
    pass


class Combat(Logic):
    pass


class Evilmonster(Logic):
    pass


class BetterTonMagicianShop(Logic):
    pass


class CantGet(Logic):
    pass


class Uberweight(Logic):
    pass


class CanRead(Logic):
    pass


class SpellScroll(Logic):
    pass


class UberWeightScroll(Logic):
    pass


class Noelves(Logic):
    pass


class PieRoom(Logic):
    pass


