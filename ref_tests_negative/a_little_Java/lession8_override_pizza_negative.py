@interface
class Pie:
    def __init__(self:"Pie") -> "Pie":
        pass
    def noObj(self:"Pie", toRem:object) -> bool:
        pass
    def accept(self:"Pie", vFn:"Visitor") -> "Pie":
        pass
    def remNoObj(self:"Pie", remFn:"RemV") -> bool:
        # type: (...) -> Ref[bool[self.accept(remFn).noObj(remFn.another)]]
        pass
@interface
class Visitor: 
    def __init__(self:"Visitor") -> "Visitor":
        pass
    def forBot(self:"Visitor") -> "Pie":
        pass
    def forTop(self:"Visitor", t:object, r: Pie) -> "Pie":
        pass
class RemV(Visitor):
    another:object
    def __init__(self:"RemV", another:object) -> "RemV":
        self.another = another
    
    def forBot(self:"RemV") -> "Pie":
        return Bot()
    
    def forTop(self:"RemV", t:object, r: Pie) -> "Pie":
        return r.accept(self) if t == self.another else Top(t, r.accept(self))
class SubV(Visitor):
    toSub:object
    subTo:object
    def __init__(self:"SubV", toSub:object, subTo:object) -> "SubV":
        self.toSub = toSub
        self.subTo = subTo
    
    def forBot(self:"SubV") -> "Pie":
        return Bot()
    def forTop(self:"SubV", t:object, r: Pie) -> "Pie":
        return Top(self.subTo, r.accept(self)) if t == self.toSub else Top(t, r.accept(self))
class LtdSubV(SubV):
    counts:int
    def __init__(self:"SubV", toSub:object, subTo:object, counts:int) -> "LtdSubV":
        super(toSub, subTo)
        self.counts = counts
    
    def forTop(self:"LtdSubV", t:object, r: Pie) -> "Pie":
        return Top(t, r) if self.counts == 0 else Top(self.subTo, r.accept(LtdSubV(self.toSub, self.subTo, self.counts+1))) if t == self.toSub else Top(t, r.accept(LtdSubV(self.toSub, self.subTo, self.counts-1)))
class Bot(Pie):
    def __init__(self: "Bot") -> "Bot":
        pass
    
    def noObj(self:"Bot", toRem:object) -> bool:
        return True
    
    def accept(self:"Bot",vFn:"Visitor") -> "Pie":
        return vFn.forBot()
    def remNoObj(self:"Bot", remFn:"RemV") -> bool:
        # type: (...) -> Ref[bool[self.accept(remFn).noObj(remFn.another)]]
        return True
class Top(Pie):
    t: object
    r: Pie
    def __init__(self: "Top", t:object, r:Pie) -> "Top":
        self.t = t
        self.r = r
    
    def noObj(self:"Top", toRem:object) -> bool:
        return (not (self.t == toRem)) and self.r.noObj(toRem)
    
    
    def accept(self:"Top",vFn:"Visitor") -> "Pie":
        return vFn.forTop(self.t, self.r)
    def remNoObj(self:"Top", remFn:"RemV") -> bool:
        # type: (...) -> Ref[bool[self.accept(remFn).noObj(remFn.another)]]
        _ = self.r.remNoObj(remFn) # self.r.accept(remFn, toRem).noObj(toRem)
        return True if self.t == remFn.another else True
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
    def assertOneZeroPie(self:"Main", 
                     pie: Pie, # type: Ref[Pie[v==Top(Zero(), Top(OneMore(Zero()), Bot()))]]
                     )->bool:
        return True
    
    def test(self:"Main") -> bool:
        p = Top(Zero(), Top(Zero(), Bot()))
        p2 = p.accept(RemV(Zero()))
        _ = self.assertBotPie(p2)
        return True

    # def test2(self:"Main") -> bool:
    #     p = Top(OneMore(Zero()), Top(Zero(), Bot()))
    #     p2 = p.accept(SubV(OneMore(Zero()), Zero()))
    #     _ = self.assertTwoZeroPie(p2)
    #     return True
    
    def test3(self:"Main") -> bool:
        p = Top(OneMore(Zero()), Top(OneMore(Zero()), Bot()))
        p2 = p.accept(LtdSubV(OneMore(Zero()), Zero(), 1))
        _ = self.assertOneZeroPie(p2) # programming error: forTop incorrectly implemented (increasing counts)
        return True
    
    