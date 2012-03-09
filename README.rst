SZMUD
=====

简介
----
一个python MUD游戏, 设计参考自<MUD Game Programming>中的BetterMUD。

Entity: 实体
------------
整个游戏世界由以下实体组成：

- Account
- Character(玩家或NPC)
- Item
- Room
- Portal
- Region
- Template(用于生成Character或Item)

游戏基础
--------
游戏响应用户输入的字符形式的命令, 
解析完交给玩家对应的Character中某个Command实例执行(通过调用Command.Execute).

游戏类Game提供一些基础事件, 
比说某个角色尝试在某个房间发讲话 AttemptSay, 
某个角色进入某个通道 AttemptEnterPortal。

单个事件根据需要调用各个涉及到的实体Entity.Query(conditon)查询事件能否发生, 
再调用Entity.React(action)响应该事件, 做出反映, 
从而完成一个事件.
具体请参考Game.Say/EnterPortal方法以及BasicLogic类的实现。

用户的单条命令的功能可以与游戏功能无关的, 
也可以是由零个或多个游戏的基础事件组成, 
甚至再直接点, 直接让零个或多个实体的响应某些动作.

以下是几个比较重要的方法/函数:

- Game.PorcessEvent
- Game.ExecuteCommand
- LogicEntity.React
- Command.Execute

游戏事件Event/实体的查询条件Condition/实体的基础动作Action
----------------------------------------------------------
第一层为游戏事件, 第二层为游戏事件实现时需要查询的实体条件或者调用到基础动作.
Condition的命令已'Can'开头.

Event/Condition/Action都是像dict类型一样, 
不过很想JavaScript中的Object可以通过Object.attrname引用Object[attrname].

Event/Condition/Action三者都包含一个特别的属性type指明其类型.

+ ...
    - Error: message

+ EnterWorld: who
    - EnterRoom: who, room, portal=None
    - EnterRegion: who
    - EnterWorld: who
    - News|Welcome|TODO
+ LeaveWorld: who
    - LeaveRoom: who, room, portal=None
    - LeaveRegion: who
    - LeaveWorld: who
    - Bye|TODO
+ Announce，通知整个游戏中的在线玩家: content
    - Announce: content

+ SpawnCharacter: templateid, room
    - SpawnCharacter: character, room
+ SpawnItem: templateid, room, region
    - SpawnItem: item, room, region - 房间
    - SpawnItem: item - 角色
+ DestoryCharacter: character
    - DestoryCharacter: character
    - DropItem: who, item, quantity
+ DestoryItem: item
    - DestoryItem: item

+ AttemptSay，玩家在房间内说话: who, content
    - CanSay: who, content
    - Say: who, content
+ AttemptGetItem: who, item, quantity
    - CanGetItem: who, item, quantity
    - GetItem: who, item
+ AttemptDropItem: who, item, quantity
    - CanDropItem: who, item, quantity
    - DropItem: who, item
+ AttemptGiveItem: giver, receiver, item, quantity
    - CanGiveItem: character, item, quantity
    - CanReceiveItem: character, item, quantity
    - GiveItem: giver, receiver, item, quantity
        - 判断是否是接受者，接受者特殊处理

+ AttemptEnterPortal，玩家通过通道进行移动: who, portal, direction
+ AttemptTransport: who, room
+ ForceTransport: who, room
    - CanLeaveRegion/CanEnterRegion: who, region
    - CanLeaveRoom/CanEnterRoom:who, portal
    - CanEnterPortal: who, portal
    - LeaveRegion: who
    - LeaveRoom: who, portal
    - EnterPortal: who, portal
    - EnterRegion: who
    - EnterRoom: who, portal

    - cleanup
    - savedatabases
    - saveregion
    - saveplayers

    - reloaditems
    - reloadcharacters
    - reloadregion

    - reloadcommands
    - reloadlogics

命令类: Commands
----------------
以下是已经实现的部分命令

- ListItems
- Go direction
- Get [n] itemname
- Drop [n] itemname
- Quit
- Chat
- Say
- Self
- Quiet
- Shutdown
- Look
- Commands
- Announce
- Items
- SaveDatabase

TODO
----
- chat          
- announce
- vision
- command

- do
- messagelogic
- addlogic
- dellogic

- modifyattrbute, entity attr value
