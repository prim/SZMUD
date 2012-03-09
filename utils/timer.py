# encoding: utf-8

from time import localtime, strftime, time


def GetTimeMS(): 
    t = time() # 返回epoch以来的毫秒数, 浮点数，秒为单位
    s = int(t) # s = 1000 ms = 1000 * 1000 us
    ms = int((t - s) * 1000)
    return ms + s * 1000
    
def GetTimeS():
    return GetTimeMS() / 1000

def GetTimeM():
    return GetTimeMS() / 60000

def GetTimeH():
    return GetTimeMS() / 3600000

def TimeStamp():
    return strftime('%H:%M:%S', localtime())
    
def DateStamp():
    return strftime('%Y.%m.%d', localtime())


class Timer():

    def __init__(self):
        # self.m_starttime = 0
        # self.m_inittime = 0
        self.m_starttime = 0
        self.m_inittime = GetTimeMS()
        
    def Reset(self, passed=0):
        self.m_starttime = passed
        self.m_inittime = GetTimeMS()
        
    def GetMS(self):
        return (GetTimeMS() - self.m_inittime) + self.m_starttime
    
    def GetS(self):
        return self.GetMS() / 1000
    
    def GetM(self):
        return self.GetMS() / 60000
        
    def GetH(self):
        return self.GetMS() / 3600000
    
    def GetD(self):
        return self.GetMS() / 86400000
    
    def GetY(self):
        return self.GetD() / 365
    
    def GetString(self):
        y = str(self.GetY())
        d = str(self.GetD() % 365)
        h = str(self.GetH() % 24)
        m = str(self.GetM() % 60)
        s = str(self.GetS() % 60)
        ms = str(self.GetMS() % 1000)
        
        return '%s years %s days %s hours %s minutes %s seconds %s microseconds.' % (
                y, d, h, m, s, ms
            )


# def ParseWord(string, index):
#     return string.split(' ')[index]
#     
# from string import replace
# SearchAndReplace = replace ### 其余代码还是使用replace

# def StringMatchFull(o, d):
#     return o.lower() == d.lower()
#     
# def StringMatchPart(part, allstr):
#     if allstr == '':
#         return True
#     part = part.lower()
#     allstr = allstr.lower()
#     
#     while True:
#         index = allstr.find(part)
#         if index == -1:
#             return False
#         elif index == 0 or allstr[index - 1] == ' ':
#             return True
#         else:
#             allstr = allstr[index + 1:]
#             
# def MatchOnepass(container, func_match):
#     for elem in container:
#         if func_match(elem.m_name):
#             return elem
# 
# def MatchTwopass(container, func_one, fuctwo):
#     r = MatchOnepass(container, func_one)    
#     if r:
#         return r
#     else:
#         return MatchOneopass(container, func_two)
#         
# def Match(container, o, d):
#     return MatchTwopass(container, fu
