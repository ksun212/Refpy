@interface
class Expr:
    def __init__(self:"Expr") -> "Expr":
        pass
    def size(self:"Expr", 
                )->int:
        # type: (...) -> Ref[int[v>=1]]
        pass
    def subst(self:"Expr", name:int, expr: "Expr") -> "Expr":
        pass
    def substitution_nodec_size(self:"Expr", name:int, expr: "Expr") -> bool:
        # type: (...) -> Ref[bool[self.subst(name,expr).size()>=self.size()]]
        pass
class Lambda(Expr):
    v:int
    body:Expr
    def __init__(self:"Lambda", elem:int, next:"Expr") -> "Lambda":
        super().__init__()
    
    def size(self: "Lambda") -> int:
        # type: (...) -> Ref[int[v>=1]]
        n = self.body
        l = n.size()
        return 1 + l
    
    def subst(self:"Lambda", name:int, expr: Expr ) -> "Lambda":
        vv = self.v
        bb = self.body
        bb2 = bb.subst(name, expr) # error: forget to do substitution
        return Lambda(vv, bb)
    def substitution_nodec_size(self:"Lambda", name:int, expr: "Expr") -> bool:
        # type: (...) -> Ref[bool[self.subst(name,expr).size()>=self.size()]]
        _ = self.body.substitution_nodec_size(name, expr)
        return True
class App(Expr):
    e1:Expr
    e2:Expr
    def __init__(self: "App", e1:Expr, e2:Expr) -> "App":
        self.e1 = e1
        self.e2 = e2
    
    def size(self: "App") -> int:
        # type: (...) -> Ref[int[v>=1]]
        s1 = self.e1.size()
        s2 = self.e2.size()
        
        return s1 + s2
    
    def subst(self:"App", name:int, expr: Expr ) -> "App":
        return App(self.e1.subst(name, expr), self.e2.subst(name, expr))
    def substitution_nodec_size(self:"App", name:int, expr: "Expr") -> bool:
        # type: (...) -> Ref[bool[self.subst(name,expr).size()>=self.size()]]
        _ = self.e1.substitution_nodec_size(name, expr) 
        # __ = self.e2.substitution_nodec_size(name, expr) 
        return True # error: forget induction hypothesis (Line 54)
# need if
class FV(Expr):
    v:int 
    def __init__(self:"FV",v:int,) -> "FV":
        self.v = v
    
    def size(self: "FV",
               ) -> int:
        # type: (...) -> Ref[int[v>=1]]
        return 1
    
    def subst(self:"FV", name:int, expr: Expr) -> "Expr":
        return expr if name == self.v else self
    def substitution_nodec_size(self:"FV", name:int, expr: "Expr") -> bool:
        # type: (...) -> Ref[bool[self.subst(name,expr).size()>=self.size()]]
        _ = expr.size()
        return True