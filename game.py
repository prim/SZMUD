# encoding: utf-8

# TODO(Prim): 考虑是不是要移除condition

from SZMUD.databases.database import ItemDB, RoomDB, AccountDB, PortalDB, CharacterDB, RegionDB
from SZMUD.utils.jsdict import Action, Event, Condition
from SZMUD.utils.timer import Timer
from SZMUD.utils.queue import PriorityQueue
from SZMUD.databases.script import CommandDB, LogicDB

# TODO(Prim): hook sysytem
from SZMUD.event import TimeEvent

# TODO: 中毒的实现，Game.AddLogic，为实体中毒的事件，在Game.ExecuteLoop定时处理，扣血
# 在DoEvent扣除相应血量，再添加实体中毒的定时事件，形成实体持续中毒的状态

# Event.valid去定有效性，LogicEntity.KillHook()另一个定时事件失效

class Game:

    def __init__(self):
        self.players = []
        self.characters = []
        self.is_running = True

        self.timer = Timer()
        self.eventqueue = PriorityQueue()

    #------------------------------------------------------------------------------ 

    # NOTE(Prim): 基础的Event优势可以对应单条Command
    #             无论时Command或者Event的实习都需要自己检查逻辑错误，保证正确性
    def ProcessEvent(self, event, **kw):
        # 可以在这里针对event的类型写响应的处理代码
        # 也可以自定义个方法调用

        if type(event) == str:
            event = Event(event, **kw)

        if event.type == 'Announce':
            self.ReactWorldPlayers(event)

        if event.type == 'AttemptSay':
            self.Say(event)

        elif event.type == 'EnterWorld':
            self.EnterWorld(event)
        elif event.type == 'LeaveWorld':
            self.LeaveWorld(event)

        elif event.type == 'SpawnCharacter':
            self.SpawnCharacter(event)
        elif event.type == 'SpawnItem':
            self.SpawnItem(event)
        elif event.type == 'DestoryCharacter':
            self.DestoryCharacter(event)
        elif event.type == 'DestoryItem':
            self.DestoryItem(event)
        
        elif event.type == 'AttemptGetItem':
            self.GetItem(event)
        elif event.type == 'AttemptDropItem':
            self.DropItem(event)
        elif event.type == 'AttemptGiveItem':
            self.GiveItem(event)

        elif event.type == 'AttemptEnterPortal':
            self.EnterPortal(event)
        elif event.type == 'AttemptTransport':
            self.AttemptTransport(event)
        elif event.type == 'ForceTransport':
            self.ForceTransport(event)

        elif event.type == 'MessageLogic':
            self.EnterPortal(event)
        elif event.type == 'AddLogic':
            self.AttemptTransport(event)
        elif event.type == 'DelLogic':
            self.ForceTransport(event)
        else:
            pass

    def ExecuteCommand(self, player, command):
        """执行玩家的单条命令
        
        Quiet模式下玩家的发送的数据一句当作命令解析；玩家只能通过say xxx发言，不能直接发言
        普通模式下，玩家数据如果带前缀/就当作命令解析，否则就发言 
        """
        c = player
        if command == u'/':
            command = c.lastcommand
        else:
            c.lastcommand = command

        if u' ' in command:
            cmd, args = command.split(u' ', 1)
        else:
            cmd, args = command, u''
        args = args.split()

        # 普通模式的特别处理
        if not c.is_quiet and cmd[0] != u'/':
            string = [cmd]
            string.extend(args)
            self.Say(Event('AttempSay', who=c, content=u' '.join(string)))
            return 
        
        if cmd[0] == u'/':
            cmd = cmd[1:]

        try:
            cmd_i = c.FindCommand(cmd)
            if not cmd_i:
                c.React(Action('Error', message=u'输入的命令不能识别：%s' % cmd))
                return 
            cmd_i.Execute(*args)             # NOTE: !!!
        except Exception, error:
            # TODO(Prim): log error
            import traceback; traceback.print_exc() 
            c.React(Action('Error', message=u'执行命令时发生严重错误，请通知管理员。\r\n错误信息：%s' % error))
    

    #------------------------------------------------------------------------------ 

    def ReactWorldPlayers(self, action):
        for player in self.players:
            player.React(action)

    def ReactWorldCharacters(self, action):
        for character in self.characters:
            character.React(action)

    def ReactRoomCharacters(self, action, room):
        for character in room.characters:
            character.React(action)

    def ReactRoomItems(self, action, room):
        for item in room.items:
            item.React(action)

    # TODO(Prim): ActionRegion?

    #------------------------------------------------------------------------------ 

    def _GetEntity(self, entityid, type):
        if type == 'Item':
            return  ItemDB[entityid]
        elif type == 'Character':
            return CharacterDB[entityid]
        elif type == 'Room':
            return RoomDB[entityid]
        elif type == 'Region':
            return RegionDB[entityid]
        elif type == 'Portal':
            return PortalDB[entityid]
        raise Exception, u'尝试获取未知类型的实体：%s' % type

    def _DeleteItem(self, item):
        i = item
        if i.region:
            i.region.DelItem(i)
            i.room.DelItem(i)
        else:
            i.room.DelItem(i)
        i.room = None
        i.region = None 
        i.ClearHooks()
        ItemDB.Delete(i)

    def _DoJoinQuantities(self, character, keepitem):
        for item in character.items:
            if item != keepitem and item.templateid == keepitem.templateid:
                keepitem.quantity += item.quantity
                self._DeleteItem(item)
    
    #------------------------------------------------------------------------------ 

    def AddCharacter(self, c):
        self.characters.append(c)

    def AddPlayer(self, p):
        self.players.append(p)

    def RemoveCharacter(self, c):
        self.characters.remove(c)

    def RemovePlayer(self, p):
        self.players.remove(p)

    #------------------------------------------------------------------------------ 

    def Say(self, event):
        import time
        print '============in Say'
        print time.time()
        print '============in Say'
        """某个角色在某个房间中发言"""
        c = event.who
        r = c.room
        reg = c.region

        content = event.content

        if content:
            condition = Condition('CanSay', who=c, content=content)
            if c.Query(condition) and r.Query(condition) and reg.Query(condition):
                action = Action('Say', who=c, content=content)
                self.ReactRoomCharacters(action, r)

                r.React(action)
                reg.React(action)
        else:
            c.React(Action('Error', message=u'发言时必须要有内容！\r\n'))

    def EnterWorld(self, event):
        """玩家上线"""
        c = event.who
        r = c.room
        reg = c.region

        c.is_loggin = True
        self.AddCharacter(c)
        self.AddPlayer(c)
        r.AddCharacter(c)
        reg.AddCharacter(c)

        self.ReactWorldPlayers(Action('EnterWorld', who=c))
        regaction = Action('EnterRegion', who=c)
        reg.React(regaction)
        c.React(regaction)
    
        raction = Action('EnterRoom', who=c, room=r, portal=None)
        r.React(raction)
        self.ReactRoomCharacters(raction, r)
        self.ReactRoomItems(raction, r)

        c.React(Action('News'))
    
    def LeaveWorld(self, event):
        """玩家下线"""
        c = event.who
        r = c.room
        reg = c.region

        raction = Action('LeaveRoom', who=c, room=r, portal=None)
        self.ReactRoomItems(raction, r)
        self.ReactRoomCharacters(raction, r)
        r.React(raction)

        regaction = Action('LeaveRegion', who=c)
        reg.React(regaction)
        c.React(regaction)

        self.ReactWorldPlayers(Action('LeaveWorld', who=c))

        r.DelCharacter(c)
        reg.DelCharacter(c)
        self.RemovePlayer(c)
        self.RemoveCharacter(c)
        c.is_loggin = False


    def EnterPortal(self, event):
        """角色进入通道，进行移动"""
        c = event.who
        p = event.portal
        direction = event.direction
        oldroom = c.room
        newroom = p.GetDestination(c.room, direction)
        oldreg = oldroom.region
        newreg = newroom.region
        change_reg = oldreg != newreg

        if change_reg:
            lcondition = Condition('CanLeaveRegion', who=c, region=oldreg)
            econdition = Condition('CanEnterRegion', who=c, region=newreg)
            if not( 
                    oldreg.Query(lcondition) and newreg.Query(econdition) and \
                    c.Query(lcondition) and  c.Query(econdition)
                ):
                return 
        lrcondition = Condition('CanLeaveRoom', who=c, portal=p)
        ercondition = Condition('CanEnterRoom', who=c, portal=p)
        pcondition = Condition('CanEnterPortal', who=c, portal=p)
        if oldroom.Query(lrcondition) and newroom.Query(ercondition) and \
           c.Query(lrcondition) and c.Query(ercondition) and \
           c.Query(pcondition) and p.Query(pcondition):

            if change_reg:
                action = Action('LeaveRegion', who=c)
                oldreg.React(action)
                c.React(action)

            action = Action('LeaveRoom', who=c, portal=p)
            self.ReactRoomCharacters(action, oldroom)
            self.ReactRoomItems(action, oldroom)
            oldroom.React(action)

            action = Action('EnterPortal', who=c, portal=p)
            p.React(action)
            c.React(action)

            if change_reg:
                oldreg.DelCharacter(c)
                c.region = newreg
                newreg.AddCharacter(c)

            oldroom.DelCharacter(c)
            c.room = newroom
            newroom.AddCharacter(c)
           
            if change_reg:
                action = Action('EnterRegion', who=c)
                newreg.React(action)
                c.React(action)

            action = Action('EnterRoom', who=c, portal=p)
            newroom.React(action)
            self.ReactRoomCharacters(action, newroom)
            self.ReactRoomItems(action, newroom)

    def AttemptTransport(self, event):
        """角色没有借助通道，直接在房间间移动"""
        c = event.who
        newroom = event.room
        oldroom = c.room
        oldreg = oldroom.region
        newreg = newroom.region
        change_reg = oldreg != newreg

        if change_reg:
            lcondition = Condition('CanLeaveRegion', who=c, region=oldreg)
            econdition = Condition('CanEnterRegion', who=c, region=newreg)
            if not( 
                    oldreg.Query(lcondition) and newreg.Query(econdition) and \
                    c.Query(lcondition) and  c.Query(econdition)
                ):
                return 

        lrcondition = Condition('CanLeaveRoom', who=c, portal=p)
        ercondition = Condition('CanEnterRoom', who=c, portal=p)
        if oldroom.Query(lrcondition) and newroom.Query(ercondition) and \
           c.Query(lrcondition) and c.Query(ercondition):

            if change_reg:
                action = Action('LeaveRegion', who=c)
                oldreg.React(action)
                c.React(action)

            action = Action('LeaveRoom', who=c, portal=p)
            self.ReactRoomCharacters(action, oldroom)
            self.ReactRoomItems(action, oldroom)
            oldroom.React(action)

            if change_reg:
                oldreg.DelCharacter(c)
                c.region = newreg
                newreg.AddCharacter(c)

            oldroom.DelCharacter(c)
            c.room = newroom
            newroom.AddCharacter(c)
           

            if change_reg:
                action = Action('EnterRegion', who=c)
                newreg.React(action)
                c.React(action)

            action = Action('EnterRoom', who=c, portal=p)
            newroom.React(action)
            self.ReactRoomCharacters(action, newroom)
            self.ReactRoomItems(action, newroom)

    def ForceTransport(self, event):
        """角色没有借助通道，直接在房间间移动，特权，不做可行性检查"""
        # TODO(Prim): 合并函数
        c = event.who
        newroom = event.room
        oldroom = c.room
        oldreg = oldroom.region
        newreg = newroom.region
        change_reg = oldreg != newreg

        if change_reg:
            action = Action('LeaveRegion', who=c)
            oldreg.React(action)
            c.React(action)

        action = Action('LeaveRoom', who=c, portal=p)
        self.ReactRoomCharacters(action, oldroom)
        self.ReactRoomItems(action, oldroom)
        oldroom.React(action)

        if change_reg:
            oldreg.DelCharacter(c)
            c.region = newreg
            newreg.AddCharacter(c)

        oldroom.DelCharacter(c)
        c.room = newroom
        newroom.AddCharacter(c)
        
        if change_reg:
            action = Action('EnterRegion', who=c)
            newreg.React(action)
            c.React(action)

        action = Action('EnterRoom', who=c, portal=p)
        newroom.React(action)
        self.ReactRoomCharacters(action, newroom)
        self.ReactRoomItems(action, newroom)


    def GetItem(self, event):
        c = event.who
        i = event.item
        quantity = event.quantity
        r = c.room
        reg = c.region

        if i.room != c.room or i.region is None:
            raise Exception, u'该物品在一个角色身上'

        if i.is_quantity and quantity < 1:
            c.React(Action('Error', message=u'输入的数目太少！'))

        if i.is_quantity and quantity > i.quantity:
            c.React(Action('Error', message=u'输入的数目太多！'))

        condition = Condition('CanGetItem', who=c, item=i, quantity=quantity)
        if i.Query(condition) and r.Query(condition) and reg.Query(condition) and c.Query(condition):
            if i.is_quantity and quantity != i.quantity:
                newitem = ItemDB.Generate(i.templateid)
                newitem.quantity = quantity
                i.quantity -= quantity
            else:
                r.DelItem(i)
                reg.DelItem(i)
                newitem = i

            newitem.room = c
            newitem.region = None
            c.AddItem(newitem)
            
            action = Action('GetItem', who=c, item=newitem)
            r.React(action)
            self.ReactRoomCharacters(action, c.room)
            self.ReactRoomItems(action, c.room)
            newitem.React(action)

            if newitem.is_quantity:
                self._DoJoinQuantities(c, newitem)

    def DropItem(self, event):
        c = event.who
        i = event.item
        quantity = event.quantity
        r = c.room
        reg = c.region

        if i.room != c and i.region is None:
            raise Exception, u'该物品不属于你！'

        if i.is_quantity and quantity < 1:
            c.React(Action('Error', message=u'输入的数目太少！'))

        if i.is_quantity and quantity > i.quantity:
            c.React(Action('Error', message=u'输入的数目太多！'))

        condition = Condition('CanDroptem', who=c, item=i, quantity=quantity)
        if i.Query(condition) and r.Query(condition) and reg.Query(condition) and c.Query(condition):
            if i.is_quantity and quantity != i.quantity:
                newitem = ItemDB.Generate(i.templateid)
                newitem.quantity = quantity
                i.quantity -= quantity
            else:
                c.DelItem(i)
                newitem = i

            newitem.room = r
            newitem.region = reg
            r.AddItem(newitem)
            reg.AddItem(newitem)
            
            action = Action('DropItem', who=c, item=newitem, quantity=quantity)
            r.React(action)
            self.ReactRoomCharacters(action, c.room)
            self.ReactRoomItems(action, c.room)
            newitem.React(action)

            if newitem.is_quantity:
                self._DoJoinQuantities(r, newitem)

    def GiveItem(self, event):
        g = event.giver
        r = event.receiver
        i = event.item
        quantity = event.quantity

        if g.room != r.room:
            raise Exception, u'传递物品时两个角色必须在同一个房间！'
           
        if i.is_quantity and quantity < 1:
            raise Exception, u'输入的数目太少！'

        if i.is_quantity and quantity > i.quantity:
            raise Exception, u'输入的数目太多！'

        gcondition = Condition('CanGiveItem', character=r, item=i, quantity=quantity)
        rcondition = Condition('CanReceiveItem', character=g, item=i, quantity=quantity)
        if i.Query(rcondition) and i.Query(gcondition) and \
           g.Query(gcondition) and g.Query(rcondition):
            
            if i.is_quantity and quantity != i.quantity:
                newitem = ItemDB.Generate(i.templateid)
                newitem.quantity = quantity
                i.quantity -= quantity
            else:
                g.DelItem(i)
                newitem = i

            newitem.room = r
            r.AddItem(newitem)
            
            self.ReactRoomCharacters(event, g.room)
            self.ReactRoomItems(event, g.room)

            if newitem.is_quantity:
                self._DoJoinQuantities(r, newitem)

    def SpawnItem(self, event):
        """为某个房间/人物刷新物品"""
        i = ItemDB.Generate(event.templateid)
        if event.region:
            r = event.room
            reg = event.region
            i.room = r
            i.region = reg
            r.AddItem(i)
            reg.AddItem(i)

            del event.templateid
            event.item = i
            r.React(event)
            reg.React(event)
        else:
            c = event.room
            i.room = c
            i.region = None
            c.AddItem(i)

            del event.templateid
            del event.region
            del event.room
            event.item = i
            c.React(event)

    def DestoryItem(self, event):
        """销毁单件物品
        
        物品可以是在人物的身上，比如说用来实现定时自动消散的物品
        """
        i = event.i

        if not i.region:
            c = i.room
            i.React(event)
            c.React(event)
        else:
            i.React(event)
            i.room.React(event)
            i.region.React(event)
        self._DeleteItem(i)
    

    def SpawnCharacter(self, event):
        """"在某个房间刷新NPC"""
        c = CharacterDB.Generate(event.templateid)
        r = event.room
        reg = r.region

        c.rooom = r
        c.region = reg
        r.AddCharacter(c)
        reg.AddCharacter(c)

        action = Action('SpawnCharacter', character=c)
        r.DoAction(action)
        reg.DoAction(action)

    def DestoryCharacter(self, event):
        """删除单个NPC, NPC身上物品掉落房间内"""
        c = event.character
        r = c.room
        reg = c.region

        if c.IsPlayer():
            raise Exception, u'不可以删除玩家！'

        c.React(event)
        r.React(event)
        reg.React(event)

        for i in c.items:
            r.AddItem(i)
            reg.AddItem(i)
            i.room = r
            i.region = reg
            
            action = Action('DropItem', who=c, item=i, quantity=i.quantity)
            r.React(action)
            reg.React(action)

        r.DelCharacter(c)
        reg.DelCharacter(c)

        c.ClearHooks()
        c.room = None
        c.region = None
        CharacterDB.Erase(c)

    #------------------------------------------------------------------------------ 

    # def LogicAction(self, entityid, type_, logicname, action):
    #     """触发特定实体的提定逻辑"""
    #     e = self._GetEntity(entityid, type_)

    #     # TODO(Prim): 
    #     logic = e.GetLogic(logicname)
    #     logic.Execute(action)

    # def AddLogic(self, entityid, logicname):
    #     """为特定实体添加提定逻辑"""
    #     e = self._GetEntity(entityid, type_)
    #     e.AddLogic(logicname)
    # 
    # def DeleteLogic(self, entityid, logicname):
    #     """为特定实体删除提定逻辑"""
    #     e = self._GetEntity(entityid, type_)
    #     e.Deletelogic(logicname)

    #------------------------------------------------------------------------------ 
    # public misc
    def ShutDown(self):
        self.is_running = False

    def CleanUp(self):
        ItemDB.CleanUp()
        CharacterDB.ClearnUp()

    def SaveAll(self):
        AccountDB.Save()
        CharacterDB.SavePlayers()
        RegionDB.SaveAll()
        
        # TODO(Prim): 
        # self.SaveTimers()

    def LoadAll(self):
        CharacterDB.LoadTemplates()
        ItemDB.LoadTemplates()

        CommandDB.Load()
        LogicDB.Load()

        RegionDB.LoadAll()
        CharacterDB.LoadPlayers()
        
        AccountDB.Load()

        # TODO(Prim): 
        # self.LoadTimers()

    def SavePlayers(self):
        AccountDB.Save()
        CharacterDB.SavePlayers()

    def SaveSingleRegion(self, regionid):
        RegionDB.SaveRegion(regionid)

    # def ReloadItemTemplates(self, filename):
    #     ItemDB.LoadTemplates(filename)

    # def ReloadCharacterTempaltes(self, filename):
    #     CharacterDB.LoadTemplates(filename)

    # def ReloadRegion(self, filename):
    #     RegionDB.LoadRegion(filename)

    # def ReloadCommandScript(self, filename, mode):
    #     pass

    # def ReloadLogicSript(self, filename, mode):
    #     pass

    def LoadTimers(self):
        pass

    def SaveTimers(self):
        pass

    def _GetTime(self):
        return self.timer.GetS()

    #------------------------------------------------------------------------------ 

    # NOTE(Prim): 对于定时事件，你无法预知未来会怎么样
    #             你约定的处理方法所需要的各个实体可能都会不再存在

    # TODO(Prim): 
    # def AddEventAbsolute(self, time, event):
    #     # 某个游戏时间发生某个事件
    #     pass

    def AddEventRelative(self, second, event, **kw):
        if kw:
            tevent = TimeEvent(self._GetTime()+second, event, **kw)
        else:
            tevent = TimeEvent(self._GetTime()+second, event)
        self.eventqueue.push(tevent)
        tevent.Hook()


    def ExecuteLoop(self):
        time = self._GetTime()
        for tevent in self.eventqueue:
            if tevent.time < time and tevent.is_valid:
                tevent.Unhook()
                game.ProcessEvent(tevent.event)
            else:
                self.eventqueue.push(tevent)
                break


game = Game()
