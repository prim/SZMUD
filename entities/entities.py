# -*- coding: utf-8 -*-

from SZMUD.entities.entity import Entity, accesslevel, LogicEntity, \
                                  InRegion, InRoom,  \
                                  HasTemplate, HasCharacters, HasItems, \
                                  HasRooms, HasPortals, HasAttributes
from SZMUD.databases.script import CommandDB


class Account(Entity, HasCharacters):

    def __init__(self):
        Entity.__init__(self)
        HasCharacters.__init__(self)
        
        self.password = u'UNDEFINED'
        self.logintime = 0
        self.accesslevel = accesslevel['Player']
        self.allowedcharacters = 2
        self.is_banned = 0

    def Load(self, stream):
        stream.ls(); self.name = stream.ls()
        stream.ls(); self.password = stream.ls()
        stream.ls(); self.logintime = stream.li()
        stream.ls(); self.accesslevel = stream.ls()
        self.accesslevel = accesslevel[self.accesslevel]
        stream.ls(); self.allowedcharacters = stream.li()
        stream.ls(); self.is_banned = stream.li()
        
        stream.ls();
        for id in stream.ll().strip().split():
            self.AddCharacter(_GetDB('Character')[int(id)])
    
    def Save(self, stream):
        def alvl(i):
            for k, v in accesslevel.items():
                if v == i:
                    return k
                    
        stream.ss('[NAME]                  ').sl(self.name).endl()
        stream.ss('[PASS]                  ').sl(self.password).endl()
        stream.ss('[FIRSTLOGINTIME]        ').si(self.logintime).endl()
        stream.ss('[ACCESSLEVEL]           ').ss(alvl(self.accesslevel)).endl()
        stream.ss('[ALLOWEDCHARS]          ').si(self.allowedcharacters).endl()
        stream.ss('[BANNED]                ').si(self.is_banned).endl()
        stream.ss('[CHARACTERS]            ')
        stream.sl(' '.join([str(c.id) for c in self.characters])).endl()
        

class Room(
        LogicEntity, 
        InRegion, HasAttributes, HasCharacters, HasItems, HasPortals
    ):

    def __init__(self):
        LogicEntity.__init__(self)
        HasAttributes.__init__(self)
        InRegion.__init__(self)
        HasCharacters.__init__(self)
        HasItems.__init__(self)
        HasPortals.__init__(self)
        
    def Add(self):
        if self.region and self.id:
            self.region.AddRoom(self)
        
    def Remove(self):
        if self.region and self.id:
            self.region.DelRoom(self)
        
    def Load(self, stream):
        self.Remove()
        
        stream.ls(); reg = stream.li()
        if reg:
            self.region = _GetDB('Region')[reg]
        else:
            self.region = None
        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()
        self.attributes.Load(stream)
        self.logics.Load(stream, id)
        
        self.Add()
    
    def Save(self, stream):
        stream.ss("[REGION]                ")
        if self.region:
            stream.si(self.region.id).endl()
        else:
            stream.si(0).endl()
        stream.ss('[NAME]                  ').sl(self.name).endl()
        stream.ss('[DESCRIPTION]           ').sl(self.description).endl()
        self.attributes.Save( stream );
        stream.endl()
        self.logics.Save( stream );


class _Portalentry:

    def __init__(self):
        self.startroom = 0
        self.destinationroom = 0
        self.directionname = ''
    
    def Load(self, stream):
        stream.ls(); self.startroom = stream.li()
        stream.ls(); self.directionname = stream.ll()
        stream.ls(); self.destinationroom = stream.li()
        
    def Save(self, stream):
        stream.ss("    [STARTROOM]             ").si(self.startroom).endl()
        stream.ss("    [DIRECTION]             ").ss(self.directionname + "\n")
        stream.ss("    [DESTROOM]              ").si(self.destinationroom).endl()
        

# TODO(Prim): 通道的设计调整 
class Portal(
        LogicEntity, 
        HasAttributes, InRegion
    ):
    """通道/道路：两个方向，1个方向为单个_Portalentry"""

    def __init__(self):
        HasAttributes.__init__(self)
        InRegion.__init__(self)
        LogicEntity.__init__(self)

        self.portals = []

    def GetDestination(self, room, directionname):
        for p in self.portals:
            if p.startroom == room.id and directionname.lower() in p.directionname.lower():
                return _GetDB('Room')[p.destinationroom]
        raise Exception, u'GetDestination() - 找不到目标房间'
            
    def Load(self, stream):
        self.Remove()
        
        stream.ls(); reg = stream.li()
        if reg:
            self.region = _GetDB('Region')[reg]
        else:
            self.region = None

        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()
        
        self.portals = []
        temp = stream.ls()
        while temp != "[/ENTRIES]":
            e = _Portalentry()
            e.Load(stream)
            stream.ls()
            temp = stream.ls()
            self.portals.append(e)
            
        self.attributes.Load(stream)
        self.logics.Load(stream, self)
        
        self.Add()
        
    def Save(self, stream):
        stream.ss("[REGION]                ")
        if self.region:
            stream.si(self.region.id).endl()
        else:
            stream.si(0).endl()

        stream.ss("[NAME]                  ").sl(self.name).endl()
        stream.ss("[DESCRIPTION]           ").sl(self.description).endl()
        
        for p in self.portals:
            stream.ss("[ENTRY]\n"); p.Save(stream); stream.ss("[/ENTRY]\n")
        stream.ss("[/ENTRIES]\n")
        
        self.attributes.Save(stream)
        self.logics.Save(stream)
        stream.endl()
        
    def Add(self):
        if self.region:
            self.region.AddPortal(self)
            
        for p in self.portals:
            r = _GetDB('Room')[p.startroom]
            r.AddPortal(self)
            
    def Remove(self):
        if self.region:
            reg = _GetDB('Region')[self.region]
            reg.DelPortal(self)
            
        for p in self.portals:
            r = _GetDB('Room')[p.startroom]
            r.DelPortal(self)


class ItemTemplate(Entity, HasAttributes):

    def __init__(self):
        Entity.__init__(self)
        HasAttributes.__init__(self)

        self.quantity = 0
        self.is_quantity = 0
        self.logics = [] # logic name strings
        
    def Load(self, stream):
        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()
        stream.ls(); self.is_quantity = stream.li()
        stream.ls(); self.quantity = stream.li()
        self.attributes.Load(stream)
        
        stream.ls()
        logic = stream.ls()
        while logic != "[/LOGICS]":
            self.logics.append(logic)
            logic = stream.ls()


class Item(
        LogicEntity, 
        HasAttributes, InRoom, InRegion, HasTemplate
    ):

    def __init__(self):
        LogicEntity.__init__(self)
        HasAttributes.__init__(self)
        InRoom.__init__(self)
        InRegion.__init__(self)
        HasTemplate.__init__(self)

        self.quantity = 1
        self.is_quantity = 0
        
    # TODO(Prim): 改成property
    def Name(self):
        if self.is_quantity:
            return self.name.replace(u'<#>', unicode(self.quantity))
        else:
            return self.name
    
    def LoadTemplate(self, template):
        self.templateid = template.id
        self.name = template.name
        self.description = template.description
        self.is_quantity = template.is_quantity
        self.quantity = template.quantity
        self.attributes = template.attributes
        
        for logicname in template.logics:
            self.AddLogic(logicname)
            
    def Load(self, stream):
        self.Remove()
        
        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()

        stream.ls(); r = stream.li()
        stream.ls(); reg = stream.li()
        if reg:
            self.region = _GetDB('Region')[reg]
            self.room = _GetDB('Room')[r]
        else:
            self.region = None
            self.room = _GetDB('Character')[r]

        stream.ls(); self.is_quantity = stream.li()
        stream.ls(); self.quantity = stream.li()
        stream.ls(); self.templateid = stream.li()
        
        self.attributes.Load(stream)
        self.logics.Load(stream, self)
        
        self.Add()
    
    def Save(self, stream):
        stream.ss("[NAME]                  ").sl(self.name).endl()
        stream.ss("[DESCRIPTION]           ").sl(self.description).endl()
        stream.ss("[ROOM]                  ").si(self.room.id).endl()
        stream.ss("[REGION]                ")
        if self.region:
            stream.si(self.region.id).endl()
        else:
            stream.si(0).endl()
        stream.ss("[ISQUANTITY]            ").si(self.is_quantity).endl()
        stream.ss("[QUANTITY]              ").si(self.quantity).endl()
        stream.ss("[TEMPLATEID]            ").si(self.templateid).endl()

        self.attributes.Save(stream)
        self.logics.Save(stream)
        stream.endl()
        
    def Add(self):
        # NOTE: 当self.region == None时，物品处于角色身上 
        if not self.room:
            return 
        if not self.region:
            self.room.AddItem(self)
        else:
            self.region.AddItem(self)
            self.room.AddItem(self)
            
    def Remove(self):
        if not self.room:
            return 
        if not self.region:
            self.room.DelItem(self)
        else:
            self.region.DelItem(self)
            self.room.DelItem(self)


class CharacterTemplate(Entity, HasAttributes):

    def __init__(self):
        Entity.__init__(self)
        HasAttributes.__init__(self)
        self.commands = [] # names
        self.logics = [] # names
        
    def Load(self, stream):
        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()

        self.attributes.Load(stream)
        
        stream.ls()
        cmd = stream.ls()
        while cmd != "[/COMMANDS]":
            self.logics.append(cmd)
            cmd = stream.ls()
            
        stream.ls()
        logic = stream.ls()
        while logic != "[/LOGICS]":
            self.logics.append(logic)
            logic = stream.ls()


class Character(
        LogicEntity, 
        HasAttributes, InRoom, InRegion, HasTemplate, HasItems
    ):

    def __init__(self):
        LogicEntity.__init__(self)
        HasAttributes.__init__(self)
        InRoom.__init__(self)
        InRegion.__init__(self)
        HasTemplate.__init__(self)
        HasItems.__init__(self)
        
        self.is_loggin = False
        self.lastcommand = ''
        self.commands = []
        
        self.account = None
        self.is_quiet = 0
        self.is_verbose = 0
         
    def LoadTemplate(self, template):
        """从模板中复制基础属性"""
        self.templateid = template.id
        self.name = template.name
        self.description = template.description
        self.attributes = template.attributes
        
        for logic in template.logics:
            self.AddLogic(logic)
             
        for cmd in template.commands:
            self.AddCommand(cmd)
                        
    def Load(self, stream):
        if self.account and self.is_loggin:
            self.Remove()
        
        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()
        stream.ls(); self.room = _GetDB('Room')[stream.li()]
        stream.ls(); reg = stream.li()
        if reg:
            self.region = _GetDB('Region')[reg]
        else:
            self.region = None
        stream.ls(); self.templateid = stream.li()
        stream.ls(); self.account = stream.li()
        stream.ls(); self.is_quiet = stream.li()
        stream.ls(); self.is_verbose = stream.li()
        
        self.attributes.Load(stream)
        
        stream.ls(); cmdname = stream.ls()
        while cmdname != '[/COMMANDS]':
            self.AddCommand(cmdname)
            self.commands[-1].Load(stream)
            cmdname = stream.ls()
            
        self.logics.Load(stream, self)
        
        stream.ls(); i = stream.ls()
        while i != '[/ITEMS]':
            _GetDB('Item').LoadEntity(stream)
            stream.ls(); i = stream.ls()
        
        if not self.account or self.is_loggin:
            self.Add()
    
    def Save(self, stream):
        stream.ss("[NAME]                  ").sl(self.name).endl()
        stream.ss("[DESCRIPTION]           ").sl(self.description).endl()
        stream.ss("[ROOM]                  ").si(self.room.id).endl()
        stream.ss("[REGION]                ")
        if self.region:
            stream.si(self.region.id).endl()
        else:
            stream.si(0).endl()
        stream.ss("[TEMPLATEID]            ").si(self.templateid).endl()
        # TODO(Prim): 考虑把self.account改成非id
        stream.ss("[ACCOUNT]               ").si(self.account).endl()
        stream.ss("[QUIETMODE]             ").si(self.is_quiet).endl()
        stream.ss("[VERBOSEMODE]           ").si(self.is_verbose).endl()

        self.attributes.Save(stream)
        
        stream.ss('[COMMANDS]\n')
        for cmd in self.commands:
            stream.ss(cmd.name).endl()
            cmd.Save(stream)
        stream.ss('[/COMMANDS]\n')
         
        self.logics.Save(stream)
        
        stream.ss('[ITEMS]\n')
        for i in self.items:
            stream.ss('[ITEM]\n')
            _GetDB('Item').SaveEntity(stream, i)
            stream.ss('[/ITEM]\n')
        stream.ss('[/ITEMS]\n')

    def FindCommand(self, cmdname):
        for cmd in self.commands:
            if cmd.name.lower() == cmdname.lower():
                return cmd

        for cmd in self.commands:
            if cmd.name.lower().startswith(cmdname.lower()):
                return cmd

    def AddCommand(self, cmdname):
        if self.HasCommand(cmdname):
            return False
        self.commands.append(CommandDB.Generate(cmdname, self))
        return True

    def DelCommand(self, cmdname):
        cmd = self.FindCommand(cmdname)
        if cmd:
            self.commands.remove(cmd)
            return True
        return False

    def HasCommand(self, cmdname):
        for cmd in self.commands:
            if cmd.name == cmdname:
                return True
        return False

    def Add(self):
        self.region.AddCharacter(self)
        self.room.AddCharacter(self)
        
    def Remove(self):
        if self.region and self.room:
            self.region.DelCharacter(self)
            self.room.DelCharacter(self)

    def IsPlayer(self):
        return self.account


class Region(
        LogicEntity, 
        HasAttributes, HasCharacters, HasItems, HasRooms, HasPortals
    ):

    def __init__(self):
        LogicEntity.__init__(self)
        HasAttributes.__init__(self)
        HasCharacters.__init__(self)
        HasRooms.__init__(self)
        HasItems.__init__(self)
        HasPortals.__init__(self)

        self.diskname = ''
        
    def Load(self, stream):
        stream.ls(); self.name = stream.ll()
        stream.ls(); self.description = stream.ll()

        self.attributes.Load(stream)
        self.logics.Load(stream, self)
    
    def Save(self, stream):
        stream.ss("[NAME]                  ").sl(self.name).endl()
        stream.ss("[DESCRIPTION]           ").sl(self.description).endl()

        self.attributes.Save(stream)
        self.logics.Save(stream)


def _GetDB(typename):
    from SZMUD.databases.database import ItemDB, RoomDB, AccountDB, PortalDB, CharacterDB, RegionDB
    if typename == 'Item':
        return ItemDB
    elif typename == 'Room':
        return RoomDB
    elif typename == 'Account':
        return AccountDB
    elif typename == 'Portal':
        return PortalDB
    elif typename == 'Character':
        return CharacterDB
    elif typename == 'Region':
        return RegionDB
