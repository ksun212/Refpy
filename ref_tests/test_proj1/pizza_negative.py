from interfaces.pizza_interface import Pizza
    
class Crust(Pizza):
    def __init__(self: "Crust") -> "Crust":
        pass
    
    def noA(self: "Crust") -> bool:
        return True
    
    def price(self:"Crust") -> int:
        # type: (...) -> Ref[int[v>0]]
        return 0
    
    def remA(self: "Crust") -> "Pizza":
        return Crust()
    def remA_idempotent(self: "Crust") -> bool:
        # type: (...) -> Ref[bool[self.remA().remA() == self.remA()]]
        return True
    def remA_noA(self: "Crust") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        return True
    def remA_noinc_price(self: "Crust") -> bool:
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
    
    def remA(self: "Cheese") -> "Pizza":
        pp = self.p
        pa = pp.remA()
        return Cheese(pa)
    def remA_idempotent(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.remA().remA() == self.remA()]]
        _ = self.p.remA_idempotent()
        return True
    def remA_noA(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        _ = self.p.remA_noA()
        return True
    def remA_noinc_price(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        _ = self.p.remA_noinc_price() # self.p.price()>=self.p.remA().price()
        __ = self.price() # self.price() >= self.p.price()
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
    def remA_idempotent(self: "Anchovy") -> bool:
        # type: (...) -> Ref[v[self.remA().remA() == self.remA()]]
        _ = self.p.remA_idempotent()
        return True
    def remA_noA(self: "Anchovy") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        _ = self.p.remA_noA()
        return True
    def remA_noinc_price(self: "Anchovy") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        _ = self.p.remA_noinc_price() # self.p.price()>=self.p.remA().price()
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
    def assertSingleCheesePizza(self: "Main", 
                                x: "Pizza", # type: Ref[Pizza[v == Cheese(Crust())]]
        ) -> int:
        return 0
    def assertEQ(self: "Main", x:"Pizza", 
             y:"Pizza", # type: Ref[Pizza[v == x]]
             ) -> int:
        return 0
    def test1(self: "Main")-> int:
        p1 = Anchovy(Cheese(Crust())).remA()
        f = self.assertSingleCheesePizza(p1)
        return 0
    def test2(self: "Main")-> int:
        f = self.assertEQ(Cheese(Anchovy(Cheese(Crust()))).remA(), Cheese(Anchovy(Cheese(Crust()))).remA().remA())
        return 0
