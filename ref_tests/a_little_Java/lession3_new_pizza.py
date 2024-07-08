@interface
class Pizza:
    def __init__(self: "Pizza") -> "Pizza":
        pass
    def remA(self: "Pizza") -> "Pizza":
        pass
    def noA(self: "Pizza") -> bool:
        pass
    def price(self:"Pizza") -> int:
        # type: (...) -> Ref[bool[v>0]]
        pass
    def theorem1(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.remA().remA() == self.remA()]]
        pass
    def theorem2(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        pass
    def theorem3(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        pass
    
class Crust(Pizza):
    def __init__(self: "Crust") -> "Crust":
        pass
    
    def noA(self: "Crust") -> bool:
        return True
    def price(self:"Crust") -> int:
        # type: (...) -> Ref[bool[v==1]]
        return 1
    
    def remA(self: "Crust") -> "Crust":
        return Crust()
    def theorem1(self: "Crust") -> bool:
        # type: (...) -> Ref[bool[self.remA().remA() == self.remA()]]
        return True
    def theorem2(self: "Crust") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        return True
    def theorem3(self: "Crust") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        _ = self.price()
        __ = self.remA().price()
        return True
class Cheese(Pizza):
    p = None # type: Ref[Pizza[true]]
    def __init__(self: "Cheese", _p: Pizza) -> "Cheese":
        self.p = _p
    
    def noA(self: "Cheese") -> bool:
        return self.p.noA()
    def price(self: "Cheese") -> int:
        # type: (...) -> Ref[int[v>0 and v==self.p.price()+1]]
        pp = self.p
        pa = pp.price()
        return pa + 1
    
    def remA(self: "Cheese") -> "Cheese":
        pp = self.p
        pa = pp.remA()
        return Cheese(pa)
    def theorem1(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.remA().remA() == self.remA()]]
        _ = self.p.theorem1()
        return True
    def theorem2(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        _ = self.p.theorem2()
        return True
    def theorem3(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        _ = self.p.theorem3() # self.p.price()>=self.p.remA().price()
        __ = self.price() # self.price() >= self.p.price()
        # self.remA() == Cheese(self.p.remA())
        # self.remA().price()>=self.remA().p.price() == self.p.remA().price()
        ___ = self.remA()
        ____ = ___.price()
        return True
class Anchovy(Pizza):
    p = None # type: Ref[Pizza[true]]
    def __init__(self: "Anchovy", _p: Pizza) -> "Anchovy":
        self.p = _p
    
    def noA(self: "Anchovy") -> bool:
        return False
    def price(self: "Anchovy") -> int:
        # type: (...) -> Ref[int[v>0 and v>=self.p.price()]]
        pp = self.p
        pa = pp.price()
        return pa
    
    def remA(self: "Anchovy") -> Pizza:
        pp = self.p
        pa = pp.remA()
        return pa
    def theorem1(self: "Anchovy") -> bool:
        # type: (...) -> Ref[v[self.remA().remA() == self.remA()]]
        _ = self.p.theorem1()
        return True
    def theorem2(self: "Anchovy") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        _ = self.p.theorem2()
        return True
    def theorem3(self: "Anchovy") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        _ = self.p.theorem3() # self.p.price()>=self.p.remA().price()
        __ = self.price() # self.price() >= self.p.price()
        # self.remA().price()==self.p().remA().price()
        return True
class MagicAnchovy(Anchovy):
    def __init__(self: "MagicAnchovy", _p: Pizza) -> "MagicAnchovy":
        self.p = _p
    def price(self: "MagicAnchovy") -> int:
        # type: (...) -> Ref[bool[v>0 and v>pa]]
        pp = self.p
        pa = pp.price()
        return pa + 1
    
class Main:
    def __init__(self: "Main") -> "Main":
        pass
    def assertDoubleCheesePizza(self: "Main", 
                                x: "Pizza", # type: Ref[Pizza[v == Cheese(Cheese(Crust()))]]
        ) -> bool:
        return True
    def assertEQ(self: "Main", x:"Pizza", 
             y:"Pizza", # type: Ref[Pizza[v == x]]
             ) -> bool:
        return True
    def test1(self: "Main")-> int:
        f = self.assertDoubleCheesePizza(Cheese(Anchovy(Cheese(Crust()))).remA())
        return 0
    def test2(self: "Main")-> int:
        f = self.assertEQ(Cheese(Anchovy(Cheese(Crust()))).remA(), Cheese(Anchovy(Cheese(Crust()))).remA().remA())
        return 0
