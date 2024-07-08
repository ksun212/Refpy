
@interface
class Pizza:
    def __init__(self: "Pizza", remFn: "RemA") -> "Pizza":
        pass
    def remA(self: "Pizza") -> "Pizza":
        pass
    
class RemA:
    def __init__(self: "RemA") -> "RemA":
        pass
    
    def forCrust(self: "RemA") -> "Pizza":
        return Crust(self) 
    
    def forCheese(self: "RemA", pp: "Pizza") -> "Pizza":
        pa = pp.remA()
        return Cheese(self, pa)
    
    def forAnchovy(self: "RemA", pp: "Pizza") -> "Pizza":
        pa = pp.remA()
        return pa
    

class Crust(Pizza):
    remFn = None # type: Ref[RemA[true]]
    def __init__(self: "Crust", remFn: "RemA") -> "Crust":
        self.remFn = remFn
    
    def remA(self: "Crust") -> "Pizza":
        rn = self.remFn
        return rn.forCrust()
class Cheese(Pizza):
    remFn = None # type: Ref[RemA[true]]
    p = None # type: Ref[Pizza[true]]
    def __init__(self: "Cheese", remFn: "RemA", _p: Pizza) -> "Cheese":
        self.remFn = remFn
        self.p = _p

    
    def remA(self: "Cheese") -> Pizza:
        rn = self.remFn
        pp = self.p
        return rn.forCheese(pp)

class Anchovy(Pizza):
    remFn = None # type: Ref[RemA[true]]
    p = None # type: Ref[Pizza[true]]
    def __init__(self: "Anchovy", remFn: "RemA" , _p: Pizza) -> "Anchovy":
        self.remFn = remFn
        self.p = _p
    
    def remA(self: "Anchovy") -> Pizza:
        rn = self.remFn
        pp = self.p
        return rn.forAnchovy(pp)
class Main:
    def assertDoubleCheesePizza(self:"Main", 
                                x: "Pizza", # type: Ref[Pizza[v == Cheese(RemA(), Cheese(RemA(), Crust(RemA())))]]
        ) -> bool:
        return True
    def assertSingleCheesePizza(self:"Main",
                                x: "Pizza", # type: Ref[Pizza[v == Cheese(RemA(), Crust(RemA()))]]
            ) -> bool:
        return True
    def assertCrustPizza(self:"Main",
                         x: "Pizza", # type: Ref[Pizza[v == Crust(RemA())]]
            ) -> bool:
        return True  
    def test1(self:"Main") -> bool:
        r = RemA()
        a = Crust(r)
        b = Cheese(r, a)
        c = Anchovy(r, b)
        d = Cheese(r, c)
        e = d.remA()
        f = self.assertDoubleCheesePizza(e)
        return True
    