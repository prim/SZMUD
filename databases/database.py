# -*- coding: utf-8 -*-

from string import punctuation as invalidchars

from SZMUD.utils.stream import LoadStream, SaveStream
from SZMUD.entities.entities import Account, Room, Portal, Item, ItemTemplate, Character, CharacterTemplate, Region


from termcolor import colored


class Database:

    def LoadEntity(self, stream):
        print colored('> Load Single Entity', 'cyan'),
        stream.ls(); id = stream.li()
        print colored('>>>>>>>> '+str(id), 'red'),

        e = self.Create(id)
        e.Load(stream)
        print colored(e.name, 'cyan')
        return e
    
    def SaveEntity(self, stream, e):
        stream.ss("[ID]                    ").si(e.id).endl()
        e.Save(stream)
        
    def LoadDirectory(self, dirname):
        print colored('>>> Load Directory '+dirname, 'green')
        manifest = open(dirname + 'manifest')
        for fn in manifest:
            fn = fn.strip()
            if fn:
                self.LoadFile(dirname + fn.strip())
            
    def LoadFile(self, filename):
        print colored('>>> Load file '+filename, 'yellow')
        filename += '.data'
        f = LoadStream(filename)
        while f.eof():
            self.LoadEntity(f)

    def SaveFile(self, filename):
        filename += '.data'
        f = SaveStream(filename)
        for id, entity in self.container.items():
            self.SaveEntity(f, entity)
            
    def Size(self):
        return len(self.container)

    def __getitem__(self, id):
        if id in self.container:
            return self.container[id]
        raise Exception, 'Out of bounds error in dict database'

    def GetAllID(self):
        return self.container.keys()

    def Purge(self):
        self.container.clear()


class DictDatabase(Database):

    def __init__(self, entitytype):
        self.container = {}
        self.type = entitytype
        
    def IsValid(self, id):
        return id in self.container
            
    def Create(self, id):
        """新创建单个实体，仅对id赋值，其他属性默认
        
        NOTE: 所有的实体的构造函数都必须可以无参数调用
        """
        e = self.type()
        e.id = id
        self.container[id] = e
        return e
        
    def Delete(self, id):
        if self.IsValid(id):
            del self.container[id]
        else:
            raise Exception, 'Out of bounds error in dict database'
            
    def FindName(self, name):
        # TODO(Prim): full match then part match
        name = name.lower()
        for id, e in self.container.items():
            if e.name.lower() == name:
                return e
                
    def GetNewID(self):
        """新创建实体时返回可用的实体id
        
        NOTE：dict的key是int类型，按顺序排列
        """
        return len(self.container) + 1


class TemplateInstanceDatabase:
     
    def __init__(self, instancetype, templatetype):
        self.cleanup = set()

        self.itype = instancetype
        self.ttype = templatetype

        self.instances = DictDatabase(self.itype)
        self.templates = DictDatabase(self.ttype)
        
    def GetTemplate(self, id):
        return self.templates[id]

    def FindName(self, name):
        return self.instances.FindName(name)
     
    #------------------------------------------------------------------------------     
     
    def Generate(self, templateid):
        """根据模板id生出实体实例"""
        id = self.instances.GetNewID()
        e = self.instances.Create(id)
        e.LoadTemplate(self.GetTemplate(templateid))
        return e
     
    #------------------------------------------------------------------------------     
     
    def Delete(self, intanceid):
        """根据模板id生出实体实例
        
        NOTE：并不实际删除，只是做标记，等待Cleanup调用后才实际删除
        """
        self.cleanup.add(intanceid)
        
    def Cleanup(self):
        for id in self.cleanup:
            self.instances.Delete(id)
            self.cleanup.remove(id)
     
    #------------------------------------------------------------------------------     
     
    def LoadEntityTemplate(self, stream):
        self.template.LoadEntity(stream)
    
    def SaveEntityTemplate(self, stream):
        self.template.SaveEntity(stream)
        
    def LoadEntity(self, stream):
        self.instances.LoadEntity(stream)
        
    def SaveEntity(self, stream, entity):
        self.instances.SaveEntity(stream, entity)
        
    def Purge(self):
        self.templates.Purge()
        self.instances.Purge()
        
    def LoadFile(self, filename):
        self.instances.LoadFile(filename)
        
    def SaveFile(self, filename):
        self.instances.SaveFile(filename)

    #------------------------------------------------------------------------------ 

    def IsValid(self, id):
        return id not in self.cleanup and self.instances.IsValid(id)

    def __getitem__(self, id):
        if id not in self.cleanup:
            return self.instances.container[id]
        raise Exception, 'Template Instance Database: Cleaned Up Item Reference!'

    def GetAllID(self):
        return self.instances.container.keys()

#------------------------------------------------------------------------------

class AccountDatabase(DictDatabase):

    def __init__(self):
        DictDatabase.__init__(self, Account)
    
    def CreateNewAccount(self, name, password):
        id = self.GetNewID()
        self.container[id] = self.type()
        self.container[id].id= id
        self.container[id].name = name
        self.container[id].password = password
        self.container[id].logintime = 0 # TODO
        return self.container[id]
        
    def Load(self):
        self.LoadDirectory('data/accounts/')
    
    def Save(self):
        dir = 'data/accounts/'
        manifest = open(dir+'manifest', 'w')
        accounts = []
        for id, entity in self.container.items():
            filename = dir + entity.name + '.data'
            f = SaveStream(filename)
            self.SaveEntity(f, entity)
            accounts.append(entity.name)
        manifest.write('\n'.join(accounts))
        manifest.close()
            
    def IsAcceptName(self, name):
        for char in name:
            if char in invalidchars:
                return False
        if not name[0].isalpha():
            return False
        if 3 > len(name) or len(name) > 26:
            return False
        return True


class RoomDatabase(DictDatabase):
    
    def __init__(self):
        DictDatabase.__init__(self, Room)


class PortalDatabase(DictDatabase):

    def __init__(self):
        DictDatabase.__init__(self, Portal)


class ItemDatabase(TemplateInstanceDatabase):

    def __init__(self):
        TemplateInstanceDatabase.__init__(self, Item, ItemTemplate) 

    def LoadTemplates(self):
        self.templates.LoadDirectory('data/templates/items/')

    def LoadTemplatesFromFile(self, filename):
        self.templates.LoadFile('data/templates/items/'+filename)
    

class CharacterDatabase(TemplateInstanceDatabase):

    def __init__(self):
        TemplateInstanceDatabase.__init__(self, Character, CharacterTemplate) 

    def LoadTemplates(self):
        self.templates.LoadDirectory('data/templates/characters/')

    def LoadTemplatesFromFile(self, filename):
        self.templates.LoadFile('data/templates/characters/'+filename)

    def LoadPlayers(self):
        self.instances.LoadDirectory('data/players/')

    def SavePlayers(self):
        dir = 'data/players/'
        manifest = open(dir+'manifest', 'w')
        players = []
        for id, entity in self.instances.container.items():
            if entity.IsPlayer():
                filename = dir + entity.name + '.data'
                f = SaveStream(filename)
                self.SaveEntity(f, entity)
                players.append(entity.name)

        manifest.write('\n'.join(player.encode('utf-8') for player in players))
        manifest.close()
            
        # self.instances.SaveDirectory('data/templates/characters')

    def LoadSinglePlayer(self, playername):
        self.instances.LoadFile('data/players/'+playername)

    # TODO(Prim): 
    def FinadPalyerFull(self, playername):
        pass

    def FinadPalyerPart(self, playername):
        pass


class RegionDatabase(DictDatabase):

    def __init__(self):
        DictDatabase.__init__(self, Region)

    def LoadRegion(self, name):
        dir = 'data/regions/' + name + '/'
        regionfilename = dir + 'region.data'
        print colored('>>> Load file: '+regionfilename, 'yellow')
        stream = LoadStream(regionfilename)
        reg = self.LoadEntity(stream)
        reg.diskname = name
        
        print colored('>>> Load file rooms: '+dir, 'yellow')
        RoomDB.LoadFile(dir+'rooms')
        print colored('>>> Load file portal: '+dir, 'yellow')
        PortalDB.LoadFile(dir+'portals')


        # 加载所有NCP以及NCP拥有的物品
        print colored('>>> Load file characters: '+dir, 'yellow')
        CharacterDB.LoadFile(dir+'characters')

        # 加载所有独立的物品
        print colored('>>> Load file items: '+dir, 'yellow')
        ItemDB.LoadFile(dir+'items')
        
    def SaveRegion(self, regionid):
        region = RegionDB[regionid]
        workingdir = 'data/regions/' + region.diskname
        self.SaveEntity(SaveStream(workingdir+'/region.data'), region)

        stream = SaveStream(workingdir+'/rooms.data')
        for room in region.rooms:
            RoomDB.SaveEntity(stream, room)
            stream.endl()
        
        stream = SaveStream(workingdir+'/portals.data')
        for portal in region.portals:
            PortalDB.SaveEntity(stream, portal)
            stream.endl()
    
        stream = SaveStream(workingdir+'/characters.data')
        for character in region.characters:
            if not character.IsPlayer():
                CharacterDB.SaveEntity(stream, character)
                stream.endl()

        stream = SaveStream(workingdir+'/items.data')
        for item in region.items:
            ItemDB.SaveEntity(stream, item)
            stream.endl()

    def LoadAll(self):
        manifest = open('data/regions/manifest')
        for name in manifest:
            name = name.strip()
            if name:
                self.LoadRegion(name.strip())
        
    def SaveAll(self):
        for name in self.container:
            if self.container[name].id:
                self.SaveRegion(name)
    

RoomDB = RoomDatabase()
AccountDB = AccountDatabase()
PortalDB = PortalDatabase()
ItemDB = ItemDatabase()
CharacterDB = CharacterDatabase()
RegionDB = RegionDatabase()

