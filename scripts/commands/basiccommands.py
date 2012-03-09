# encoding: utf-8

from SZMUD.utils.jsdict import Action, Event
from SZMUD.scripts.commands.command import Command
from SZMUD.entities.entity import GetItemByName, GetByName
from SZMUD.databases.database import CharacterDB
from SZMUD.game import game


class Quit(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        self.me.React(Action('Quit'))


class Go(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) != 1:
            self.UsageError()
        else:
            r = self.me.room
            for ps in r.portals:
                for p in ps.portals:
                    if p.startroom == r.id and args[0].lower() in p.directionname.lower():
                        game.ProcessEvent('AttemptEnterPortal', who=self.me, portal=ps, direction=args[0])
                        return 
            self.me.React(Action('Error', message=u'Invalid diraction'))


class Test(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        print 'Test--------------------------------'
        import time
        print time.time()
        print 'Test--------------------------------'
        game.AddEventRelative(5, 'AttemptSay', who=self.me, content=u'测试演示')


class Untest(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        print 'UnTest--------------------------------'
        import time
        print time.time()
        print 'UnTest--------------------------------'
        self.me.ClearHooks()


class Chat(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) < 1:
            self.UsageError()
        game.AddEventAbsolute('chat', speaker=self.me, message=' '.join(args))


class Say(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) != 1:
            self.UsageError()
        else:
            game.ProcessEvent('AttemptSay', who=self.me, content=args[0])


class Self(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) != 0:
            self.UsageError()
        else:
            string = [
                u'姓名：%s' % self.me.name,
                u'介绍：%s' % self.me.description,
            ]
            self.me.React(Action('See', content=u'\r\n'.join(string)))
            self.me.React(Action('See', content=u'\r\n'))


class Quiet(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) == 1:
            if args[0] == 'on':
                self.me.is_quiet = 1
                self.me.React(Action('Announce', content=u'你现在处于安静模式。'))
            elif args[0] == 'off':
                self.me.is_quiet = 0
                self.me.React(Action('Announce', content=u'你现在处于一般模式。'))
            else:
                self.UsageError()
            game.ProcessEvent('AttempSay', who=self.me, content=' '.join(args))
        else:
            self.UsageError()


class Shutdown(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) > 0:
            game.ProcessEvent(Event('Announce', content=u'服务器正在关闭。%s' % ''.join(args)))
        elif len(args) == 0:
            game.ProcessEvent(Event('Announce', content=u'服务器正在关闭。'))
        game.ShutDown()


class Look(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) == 0:
            self.me.React(Action('SeeRoom'))
        else:
            self.UsageError()


class Commands(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) != 0:
            self.UsageError()
        else:
            string = [u'你可以使用一下命令:',]
            for cmd in self.me.commands:
                string.append(u'- %s' % cmd.name)
            self.me.React(Action('See', content=u'\r\n'.join(string)))
            self.me.React(Action('See', content=u'\r\n'))


class Announce(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) == 0:
            self.UsageError()
        else:
            game.ProcessEvent(Event('Announce', content=u''.join(args)))


class Get(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) < 1 or len(args) > 2:
            self.UsageError()
        else:
            r = self.me.room
            if len(args) == 2:
                quantity = int(args[0])
                name = args[1]
            else:
                quantity = 0
                name = args[0]
            i = GetItemByName(r.items, name)
            if i:
                if i.is_quantity and quantity == 0:
                    quantity = i.quantity
                game.ProcessEvent('AttemptGetItem', who=self.me, item=i, quantity=quantity)
            else:
                self.me.React(Action('Error', message=u'不存在这个物品。'))


class Items(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) != 0:
            self.UsageError()
        else:
            string = [u'你携带了这些物品:',]
            for i in self.me.items:
                string.append(u'- %s' % i.Name())
            self.me.React(Action('See', content=u'\r\n'.join(string)))
            self.me.React(Action('See', content=u'\r\n'))


class Drop(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) < 1 or len(args) > 2:
            self.UsageError()
        else:
            if len(args) == 2:
                quantity = int(args[0])
                name = args[1]
            else:
                quantity = 0
                name = args[0]
            i = GetItemByName(self.me.items, name)
            if i.is_quantity and quantity == 0:
                quantity = i.quantity
            game.ProcessEvent('AttemptDropItem', who=self.me, item=i, quantity=quantity)


class SaveDatabase(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) == 1:
            if args[0] == 'all':
                self.Announce(u'开始保存所有的数据')
                game.SaveAll()
                self.Announce(u'保存工作结束')
            # TODO(Prim): 
            # elif args[0] == 'players':
            #     self.me.React(Action('Anounce', content=u'开始保存所有的数据'))
            #     game.SaveAll()
            # elif args[0] == 'regions':
            #     self.me.React(Action('Anounce', content=u'开始保存所有的数据'))
            #     game.SaveAll()

        else:
            self.UsageError()


class AddF(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) == 1:
            name = args[0]
            c = GetByName(self.me.room.characters, name)

            if 'friends' in self.me.attributes: 
                self.me.attributes['friends'].append(c.id)
            else:
                self.me.attributes['friends'] = [c.id]
        else:
            self.UsageError()


class DelF(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) == 1:
            name = args[0]
            c = GetByName(self.me.room.characters, name)

            if 'friends' in self.me.attributes: 
                self.me.attributes['friends'].remove(c.id)
            else:
                # TODO(Prim): 
                pass
        else:
            self.UsageError()


class FS(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        string = [u'你有以下这些好友：',]
        for id in self.me.attributes['friends']:
            string.append(u'- %s' % CharacterDB[id].name)
        self.me.React(Action('See', content=u'\r\n'.join(string)))
        self.me.React(Action('See', content=u'\r\n'))


class Give(Command):
    pass

# TODO(Prim): 
class DestroyItem(Command):
    pass


class DestroyCharacter(Command):
    pass


class CleanUp(Command):
    pass



class Kick(Command):

    def __init__(self, 
            usage='', 
            description=''
        ):
        Command.__init__(self, usage, description)

    def Run(self, *args):
        if len(args) < 1:
            self.UsageError()
        else:
            game.ProcessEvent('AttempSay', who=self.me, content=' '.join(args))


class Python(Command):
    pass


class SpawnItem(Command):
    pass


class SpawnCharacter(Command):
    pass





class ReLoadCommand(Command):
    pass

class ReLoadScript(Command):
    pass

# class Action(Command):
#     pass


class North(Command):
    pass


class Pies(Command):
    pass


class Visual(Command):
    pass


class AddCommand(Command):
    pass


class DelCommand(Command):
    pass


class Emulate(Command):
    pass


class AddPlayerLogic(Command):
    pass


class DelPlayerLogic(Command):
    pass


class PythonExec(Command):
    pass




class Teleport(Command):
    pass




class LoadDatabase(Command):
    pass


class Initialize(Command):
    pass


class East(Command):
    pass


class South(Command):
    pass


class West(Command):
    pass


class NorthEast(Command):
    pass


class NorthWest(Command):
    pass


class SouthEast(Command):
    pass


class SouthWest(Command):
    pass


class Up(Command):
    pass


class Down(Command):
    pass


class NE(Command):
    pass


class NW(Command):
    pass


class SE(Command):
    pass


class SW(Command):
    pass


class SuperGlue(Command):
    pass


class UberWeight(Command):
    pass




class Receive(Command):
    pass


class Inventory(Command):
    pass


class Arm(Command):
    pass


class DisArm(Command):
    pass


class Read(Command):
    pass


class List(Command):
    pass


class Buy(Command):
    pass


class Attack(Command):
    pass


class BreakAttack(Command):
    pass
