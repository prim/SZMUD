# -*- coding: utf-8 -*-

from SZMUD.utils.jsdict import Event

        
class TimeEvent:

    def __init__(self, time, event, **kw):
        self.time = time
        self.is_valid = True

        if type(event) == str:
            self.event = Event(event, **kw)
        else:
            self.event = event

    # TODO(Prim): 漂亮一点的代码
    def Hook(self):
        if self.event.type in ['EnterWorld', 'LeaveWorld']:
            self.event.who.AddHook(self)

        elif self.event.type == 'SpawnCharacter':
            self.event.room.AddHook(self)
        elif self.event.type == 'SpawnItem':
            self.event.room.AddHook(self)
            if self.event.region:
                self.event.region.AddHook(self)
        elif self.event.type == 'DestoryCharacter':
            self.event.character.AddHook(self)
        elif self.event.type == 'DestoryItem':
            self.event.item.AddHook(self)

        elif self.event.type == 'AttemptSay':
            self.event.who.AddHook(self)
        elif self.event.type == 'AttemptGetItem':
            self.event.who.AddHook(self)
            self.event.item.AddHook(self)
        elif self.event.type == 'AttemptDropItem':
            self.event.who.AddHook(self)
            self.event.item.AddHook(self)
        elif self.event.type == 'AttemptGiveItem':
            self.event.giver.AddHook(self)
            self.event.reveiver.AddHook(self)
            self.event.item.AddHook(self)
        elif self.event.type == 'AttemptEnterPortal':
            self.event.who.AddHook(self)
            self.event.portal.AddHook(self)
        elif self.event.type == 'AttemptTransport':
            self.event.who.AddHook(self)
            self.event.room.AddHook(self)
        elif self.event.type == 'ForceTransport':
            self.event.who.AddHook(self)
            self.event.room.AddHook(self)

        elif self.event.type in ['MessageLogic', 'DelLogic']:
            self.event.entity.AddHook(self)
        
    def Unhook(self):
        self.is_valid = False
        
        if self.event.type in ['EnterWorld', 'LeaveWorld']:
            self.event.who.DelHook(self)

        elif self.event.type == 'SpawnCharacter':
            self.event.room.DelHook(self)
        elif self.event.type == 'SpawnItem':
            self.event.room.DelHook(self)
            if self.event.region:
                self.event.region.DelHook(self)
        elif self.event.type == 'DestoryCharacter':
            self.event.character.DelHook(self)
        elif self.event.type == 'DestoryItem':
            self.event.item.DelHook(self)

        elif self.event.type == 'AttemptSay':
            self.event.who.DelHook(self)
        elif self.event.type == 'AttemptGetItem':
            self.event.who.DelHook(self)
            self.event.item.DelHook(self)
        elif self.event.type == 'AttemptDropItem':
            self.event.who.DelHook(self)
            self.event.item.DelHook(self)
        elif self.event.type == 'AttemptGiveItem':
            self.event.giver.DelHook(self)
            self.event.reveiver.DelHook(self)
            self.event.item.DelHook(self)
        elif self.event.type == 'AttemptEnterPortal':
            self.event.who.DelHook(self)
            self.event.portal.DelHook(self)
        elif self.event.type == 'AttemptTransport':
            self.event.who.DelHook(self)
            self.event.room.DelHook(self)
        elif self.event.type == 'ForceTransport':
            self.event.who.DelHook(self)
            self.event.room.DelHook(self)

        elif self.event.type in ['MessageLogic', 'DelLogic']:
            self.event.entity.DelHook(self)
        
    def Save(self, stream):
        pass
    
    def Load(self, stream):
        pass

    def __cmp__(self, other):
        return cmp(self.time, other.time)
