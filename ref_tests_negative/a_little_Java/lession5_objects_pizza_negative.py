@interface
class Pie:
    def __init__(self:"Pie") -> "Pie":
        pass
    def noObj(self:"Pie", toRem:object) -> bool:
        pass
    def remObj(self:"Pie", remFn:"RemV", toRem:object) -> "Pie":
        pass
    def subObj(self:"Pie", subFn:"SubV", toSub:object, subTo:object) -> "Pie":
        pass
    def noObj_after_rem(self:"Pie", remFn:"RemV", toRem:object) -> bool:
        # type: (...) -> Ref[bool[self.remObj(remFn, toRem).noObj(toRem)]]
        pass
    def noObj_after_effective_sub(self:"Pie", subFn:"SubV", toSub:object, subTo:object) -> bool:
        # type: (...) -> Ref[bool[self.subObj(subFn, toSub, subTo).noObj(toSub) if (not toSub == subTo) else True]]
        pass
class RemV:
    def __init__(self:"RemV") -> "RemV":
        pass
    
    def forBot(self:"RemV", another:object) -> "Pie":
        return Bot()
    
    def forTop(self:"RemV", t:object, r: Pie, another:object) -> "Pie":
        return Top(t, r.remObj(self, another)) if t == another else r.remObj(self, another)
class SubV:
    def __init__(self:"SubV") -> "SubV":
        pass
    
    def forBot(self:"SubV", toSub:object, subTo:object) -> "Pie":
        return Bot()
    
    def forTop(self:"SubV", t:object, r: Pie, toSub:object, subTo:object) -> "Pie":
        return Top(subTo, r.subObj(self, toSub, subTo)) if t == toSub else Top(t, r.subObj(self, toSub, subTo))

class Bot(Pie):
    def __init__(self: "Bot") -> "Bot":
        pass
    
    def noObj(self:"Bot", toRem:object) -> bool:
        return True
    
    
    def remObj(self:"Bot",remFn:"RemV", toRem:object) -> "Pie":
        return remFn.forBot(toRem)
    def noObj_after_rem(self:"Bot", remFn:"RemV", toRem:object) -> bool:
        # type: (...) -> Ref[bool[self.remObj(remFn, toRem).noObj(toRem)]]
        return True
    
    def subObj(self:"Bot", subFn:"SubV", toSub:object, subTo:object) -> "Pie":
        return subFn.forBot(toSub, subTo)
    def noObj_after_effective_sub(self:"Bot", subFn:"SubV", toSub:object, subTo:object) -> bool:
        # type: (...) -> Ref[bool[self.subObj(subFn, toSub, subTo).noObj(toSub) if (not toSub == subTo) else True]]
        return True
class Top(Pie):
    t: object
    r: Pie
    def __init__(self: "Top", t:object, r:Pie) -> "Top":
        self.t = t
        self.r = r
    
    def noObj(self:"Top", toRem:object) -> bool:
        return (not (self.t == toRem)) and self.r.noObj(toRem)
    
    
    def remObj(self:"Top",remFn:"RemV", toRem:object) -> "Pie":
        return remFn.forTop(self.t, self.r, toRem)
    def noObj_after_rem(self:"Top", remFn:"RemV", toRem:object) -> bool:
        # type: (...) -> Ref[bool[self.remObj(remFn, toRem).noObj(toRem)]]
        _ = self.r.noObj_after_rem(remFn, toRem) # self.r.remObj(remFn, toRem).noObj(toRem)
        return True if self.t == toRem else True # programming error: RemV.forTop uses a wrong implementation
    
    def subObj(self:"Top", subFn:"SubV", toSub:object, subTo:object) -> "Pie":
        return subFn.forTop(self.t, self.r, toSub, subTo)
    def noObj_after_effective_sub(self:"Top", subFn:"SubV", toSub:object, subTo:object) -> bool:
        # type: (...) -> Ref[bool[self.subObj(subFn, toSub, subTo).noObj(toSub) if (not toSub == subTo) else True]]
        _ = self.r.noObj_after_effective_sub(subFn, toSub, subTo) # self.r.subObj(remFn, toRem).noObj(toRem)
        return True if self.t == toSub else True
@interface
class Num:
    def __init__(self:"Num") -> "Num":
        pass
class Zero(Num):
    def __init__(self: "Zero") -> "Zero":
        super().__init__()
class OneMore(Num):
    precessor: Num
    def __init__(self: "OneMore", p:Num) -> "OneMore":
        self.precessor = p
class Main:
    def __init__(self:"Main") -> "Main":
        pass
    def assertBotPie(self:"Main", 
                     pie: Pie, # type: Ref[Pie[v==Bot()]]
                     )->bool:
        return True
    def assertTwoZeroPie(self:"Main", 
                     pie: Pie, # type: Ref[Pie[v==Top(Zero(), Top(Zero(), Bot()))]]
                     )->bool:
        return True
    
    def test(self:"Main") -> bool:
        p = Top(Zero(), Top(Zero(), Bot()))
        p2 = p.remObj(RemV(), Zero())
        _ = self.assertBotPie(p2) # programming error: RemV.forTop uses a wrong implementation
        return True

    def test2(self:"Main") -> bool:
        p = Top(OneMore(Zero()), Top(Zero(), Bot()))
        p2 = p.subObj(SubV(), OneMore(Zero()), Zero())
        _ = self.assertTwoZeroPie(p2)
        return True
    
