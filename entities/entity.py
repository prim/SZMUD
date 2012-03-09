# -*- coding: utf-8 -*-

from SZMUD.databases.script import LogicDB


accesslevel = {'Player':0, 'Builder':1, 'Admin':2, 'God':3}


def GetByName(container, name):
    for entity in container:
        if name.lower() == entity.name.lower():
            return entity
    for entity in container:
        if name.lower() in entity.name.lower():
            return entity

def GetItemByName(container, name):
    for i in container:
        if name.lower() in i.Name().lower():
            return i


class Databank(dict):

    def Load(self, stream):
        t = stream.ls()
        t = stream.ls()
        while t != '[/DATABANK]':
            v = stream.ls()
            if v.isdigit():
                self[t] = int(v)
            else:
                v = v.replace('_', ' ')
                v = v.strip()
                self[t] = [int(i) for i in v.split(' ')]
            t = stream.ls()
            # self[t] = stream.li()
            # t = stream.ls()
            
    def Save(self, stream):
        stream.ss('[DATABANK]\n')
        for key, value in self.items():
            if type(value) == int:
                stream.ss(key + ' '*(24 - len(key)) + str(value)).endl()
            elif type(value) == list:
                stream.ss(key + ' '*(24 - len(key)) + '_'.join(map(str, value))+'_').endl()
        stream.ss('[/DATABANK]\n')


class HasAttributes:
    
    def __init__(self):
        self.attributes = Databank()


class Entity: 

    def __init__(self):
        self.id = 0 
        self.name = u'UNDEFINDED'
        self.description = u'UNDEFINDED'


class InRegion:

    def __init__(self):
        self.region = None


class InRoom:

    def __init__(self):
        self.room = None
        

class HasTemplate:

    def __init__(self):
        self.templateid = 0


class HasCharacters:

    def __init__(self):
        self.characters = []
    
    def AddCharacter(self, c):
        self.characters.append(c)
        
    def DelCharacter(self, c):
        self.characters.remove(c)


class HasItems:

    def __init__(self):
        self.items = []
        
    def AddItem(self, i):
        self.items.append(i)
        
    def DelItem(self, i):
        self.items.remove(i)
        

class HasRooms:

    def __init__(self):
        self.rooms = []
        
    def AddRoom(self, r):
        self.rooms.append(r)
        
    def DelRoom(self, r):
        self.rooms.remove(r)
        

class HasPortals:

    def __init__(self):
        self.portals = []
        
    def AddPortal(self, p):
        self.portals.append(p)
        
    def DelPortals(self, p):
        self.portals.remove(p)


class _LogicCollection:

    def __init__(self):
        # {logic_class_name:logic_instance}
        self.collection = Databank()

    def React(self, action):
        for logic in self.collection.values():
            if not logic.React(action):
                return False
        return True


    def Get(self, name):
        # TODO(Prim): 
        # attrs = {}
        # for attr in self.collection.keys():
        #     attrs[attr.lower()] = attr
        # if name in attrs:
        #     return self.collection[attrs[name]]
        return self.collection[name]
        
    def Add(self, name, entity, conn=None):
        logic = LogicDB.Generate(name, entity)
        self.AddExisting(logic, conn)
        
    def AddExisting(self, logic, conn=None): ### logic.name
        if conn:
            logic.connection = conn
        self.collection[logic.name] = logic 

    def Del(self, name):
        del self.collection[name]
    
    def Has(self, name):
        return name in self.collection

    def Attribute(self, cls, attr):
        """返回某个逻辑类cls实例的attr属性"""
        return self.collection[cls].Attribute[attr]

    def Load(self, stream, entity):
        stream.ls(); name = stream.ls()
        while name != '[/LOGICS]':
            self.Add(name, entity)
            self.Get(name).Load(stream) # logic.load
            name = stream.ls()
            
    def Save(self, stream):
        stream.ss('[LOGICS]\n')
        for l in self.collection.values():
            if l.CanSave():
                stream.ss(l.name).endl()
                l.Save(stream)
        stream.ss('[/LOGICS]\n')


class LogicEntity(Entity):

    def __init__(self):
        self.logics = _LogicCollection()
        self.hooks = []
        
    def React(self, action):
        return self.logics.React(action)

    Query = React

    #-------------------------------------------------------------------------

    def AddLogic(self, logicname, conn=None):
        try:
            self.logics.Add(logicname, self, conn)
            return True
        except Exception, error:
            import traceback; traceback.print_exc() 
            return False
                
    def AddExistingLogic(self, logic, conn=None):
        try:
            self.logics.AddExisting(logic, conn)
            return True
        except Exception, error:
            import traceback; traceback.print_exc() 
            return False

    def DeleteLogic(self, logicname):
        try:
            self.ClearLogicHooks(logicname)
            self.logics.Del(logicname)
            return True
        except Exception, error:
            import traceback; traceback.print_exc() 
            return False

    def GetLogic(self, logicname):
        return self.logics.Get(logicname)
        
    def HasLogic(self, logicname):
        return self.logics.Has(logicname)

    #-------------------------------------------------------------------------
    # hook system    
    # NOTE(Prim): 这套东西就来用来够住Entity和Game.Event
    #             AddHook/DelHook内部使用，程序员在编写Logic/Command时可以使用KillHook/ClearHooks/ClearLogicHooks
    
    def AddHook(self, tevent):
        self.hooks.append(tevent)
        print 'AddHook--------------------------------'
        import time
        print time.time()
        print self.hooks
        print '---------------------------------'
    
    def DelHook(self, tevent):
        self.hooks.remove(tevent)
        print 'DelHook---------------------------------'
        import time
        print time.time()
        print self.hooks
        print '---------------------------------'
        
    def KillHook(self, type):
        # 实例：entity.KillHook('AtttemptSay')
        for tevent in self.hooks:
            if tevent.event.type == type:
                tevent.Unhook()
        print 'KillHook---------------------------------'
        import time
        print time.time()
        print self.hooks
        print '---------------------------------'
        
    def ClearHooks(self):
        """清除与实体相关的所有TimeEvent"""
        for tevent in self.hooks:
            tevent.Unhook()
            
    # NOTE(Prim): 当MessageLogic/DelLogic TimeEvent只有在对应实体有响应的logic实例才是合法的
    #             如果相应的逻辑实例被删除了掉了，那么实体所有与此相关的TimeEvent都应该失效
    #             当删除实体的Logic时，必须随后调用这个方法保证正确性
    def ClearLogicHooks(self, logic):
        for tevent in self.hooks:
            # TODO(Prim): 不全logic系列事件
            if tevent.event.type == 'MessageLogic' or tevent.event.type == 'DelLogic':
                if tevent.event.name == logic.name:
                    tevent.Unhook()
