# encoding: utf-8

class PriorityQueue:

    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

    def push(self, item):
        self.items.append(item)

    def pop(self):
        maxi = 0
        for i in range(1, len(self.items)):
            if self.items[i] < self.items[maxi]:
                maxi = i
        item = self.items[maxi]
        self.items[maxi:maxi+1] = []
        return item

    def __iter__(self):
        return self

    def next(self):
        if len(self.items):
            return self.pop()
        else:
            raise StopIteration


# class Item:
# 
#     def __init__(self, level, value):
#         self.level = level
#         self.value = value
# 
#     def __cmp__(self, other):
#         return cmp(self.level, other.level)
# 
# 
# q = PriorityQueue()
# q.push(Item(3, 3))
# q.push(Item(3, 4))
# q.push(Item(2, 99))
# q.push(Item(2, 11))
# q.push(Item(1, 0))
# q.push(Item(2, 2))
# q.push(Item(3, 5))
# 
# for i in q:
#     print i.level, i.value
