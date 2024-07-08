
class Pizza:
    def __init__(self: "Pizza") -> "Pizza":
        pass
    def remA(self: "Pizza") -> "Pizza":
        pass
    def price(self:"Pizza") -> int:
        # type: (...) -> Ref[bool[v>0]]
        pass
    def remA_noinc_price(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        pass
    
class Crust(Pizza):
    def __init__(self: "Crust") -> "Crust":
        pass
    
    def price(self:"Crust") -> int:
        # type: (...) -> Ref[bool[v==1]]
        return 1
    
    def remA(self: "Crust") -> "Pizza":
        return Crust()
    def remA_noinc_price(self: "Crust") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        _ = self.price()
        __ = self.remA().price()
        return True
    
class Cheese(Pizza):
    p = None # type: Ref[Pizza[true]]
    def __init__(self: "Cheese", _p: Pizza) -> "Cheese":
        self.p = _p
    
    def price(self: "Cheese") -> int:
        # type: (...) -> Ref[int[v>0 and v==self.p.price()+1]]
        pp = self.p
        pa = pp.price()
        return pa + 1
    
    def remA(self: "Cheese") -> "Pizza":
        pp = self.p
        pa = pp.remA()
        return Cheese(pa)
    def remA_noinc_price(self: "Cheese") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        # _ = self.p.remA_noinc_price() # self.p.price()>=self.p.remA().price()
        return True