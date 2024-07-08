
@interface
class Shish:
    def __init__(self:"Shish" ) -> "Shish":
        pass
    def onlyOnions(self: "Shish") -> "bool":
        pass
class Skewer(Shish): 
    def __init__(self:"Skewer") -> "Skewer":
        pass
    
    def onlyOnions(self: "Skewer") -> "bool":
        return True
class Onion(Shish):
    s = None # type: Ref[Shish[true]]
    def __init__(self:"Onion", _s:"Shish",) -> "Onion":
        self.s = _s
    
    def onlyOnions(self: "Onion") -> "bool":
        ss = self.s
        return ss.onlyOnions()
    def onlyOnions_still_onlyOnions(self: "Onion", 
                                    _s: "Shish", # type: Ref[Shish[v.onlyOnions() == True]]
                                    ) -> "Onion":
        # type: (...) -> Ref[Onion[v.onlyOnions() == True]]
        return Onion(_s)
    
class Lamb(Shish):
    s = None # type: Ref[Shish[true]]
    def __init__(self:"Lamb", _s:"Shish",) -> "Lamb":
        self.s = _s
    
    def onlyOnions(self: "Lamb") -> "bool":
        return False
    def onlyOnions_still_false(self: "Lamb", _s: "Shish") -> "Lamb":
        # type: (...) -> Ref[Onion[v.onlyOnions() == False]]
        return Lamb(_s)
    
# a = Skewer()
# b = Onion(a)
# c = b.onlyOnions()
# d = assertTrue(c)

# a = Skewer()
# b = Lamb(a)
# c = b.onlyOnions()
# d = assertFalse(c)





@interface
class Rod:
    def __init__(self:"Rod" ) -> "Rod":
        pass
class Dagger(Rod):
    def __init__(self:"Dagger" ) -> "Dagger":
        pass
class Sabre(Rod):
    def __init__(self:"Sabre" ) -> "Sabre":
        pass
class Sword(Rod):
    def __init__(self:"Sword" ) -> "Sword":
        pass
@interface
class Kebab:
    def __init__(self:"Kebab" ) -> "Kebab":
        pass
    def whatHolder(self: "Kebab") -> object:
        pass
class Holder(Kebab):
    o = None # type: Ref[object[true]]
    def __init__(self:"Holder", _o:object,) -> "Holder":
        self.o = _o
    
    def whatHolder(self: "Holder") -> object:
        return self.o

class Shallot(Kebab):
    k = None # type: Ref[Kebab[true]]
    def __init__(self:"Shallot", _k:Kebab,) -> "Shallot":
        self.k = _k
    
    def whatHolder(self: "Shallot") -> object:
        kk = self.k
        return kk.whatHolder()
    def whatHolder2(self: "Shallot" # type: Ref[Shallot[v.k.whatHolder() == Dagger()]]
                   ) -> object:
        # type: (...) -> Ref[object[v==Dagger()]]
        kk = self.k
        return kk.whatHolder()
    def daggerStillDagger(self: "Shallot", 
                          _k: Kebab # type: Ref[Shallot[v.whatHolder() == Dagger()]]
                   ) -> "Shallot":
        # type: (...) -> Ref[Shallot[v.whatHolder()==Dagger()]]
        return Shallot(_k)
class Main:
    def __init__(self:"Main") -> "Main":
        pass
    def assertTrue(self:"Main", 
                    x: bool, # type: Ref[bool[v == True]]
        ) -> bool:
        return True
    def assertFalse(self:"Main",
                    x: bool, # type: Ref[bool[v == False]]
            ) -> bool:
        return True
    def assertDagger(self:"Main",
                     x: "Dagger", # type: Ref[Dagger[v == Dagger()]]
        ) -> bool:
        return True
    def test1(self:"Main") -> bool:
        a = Skewer()
        b = Lamb(a)
        bb = Onion(b)
        c = bb.onlyOnions()
        d = self.assertFalse(c)
        return True
    def test2(self:"Main") -> bool:
        aa = Sword()
        a = Holder(aa)
        ab = Shallot(a)
        b = ab.whatHolder()
        c = self.assertDagger(b) # programming error: use a wrong holder (Sword)
        return True
