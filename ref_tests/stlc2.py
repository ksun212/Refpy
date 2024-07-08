@interface
class Expr:
    def __init__(self:"Expr") -> "Expr":
        pass
    def size(self:"Expr", 
                )->int:
        return 0
    def subst(self:"Expr", name:int, 
             expr: "Expr", # type: Ref[Expr[v.size() == 1]]
             ) -> "Expr":
        # type: (...) -> Ref[Expr[v.size()==self.size()]]
        pass
class Lambda(Expr):
    v = None # type: Ref[int[true]]
    body = None # type: Ref[Expr[true]]
    def __init__(self:"Lambda", elem:int, next:"Expr") -> "Lambda":
        super().__init__()
    
    def size(self: "Lambda") -> int:
        n = self.body
        l = n.size()
        return 1 + l
    def subst(self:"Lambda", name:int, 
             expr: Expr, # type: Ref[Expr[v.size() == 1]]
             ) -> "Lambda":
        # type: (...) -> Ref[Lambda[v.size()==self.size()]]
        vv = self.v
        bb = self.body
        bb2 = bb.subst(name, expr)
        return Lambda(vv, bb2)
class App(Expr):
    e1 = None  # type: Ref[Expr[true]]
    e2 = None  # type: Ref[Expr[true]]
    def __init__(self: "App", _e1:Expr, _e2:Expr) -> "App":
        self.e1 = _e1
        self.e2 = _e2
        super().__init__()
    
    def size(self: "App") -> int:
        ee1 = self.e1
        ee2 = self.e2
        s1 = ee1.size()
        s2 = ee2.size()
        return s1 + s2
    def subst(self:"App", name:int, 
             expr: Expr, # type: Ref[Expr[v.size() == 1]]
             ) -> "App":
        # type: (...) -> Ref[App[v.size()==self.size()]]
        ee1 = self.e1
        ee1_ = ee1.subst(name, expr)
        ee2 = self.e2
        ee2_ = ee2.subst(name, expr)
        return App(ee1_, ee2_)
    
# def fresh(v:int, # type: Ref[int]
#           ) -> bool:
#     pass
# need if
class FV(Expr):
    v = None # type: Ref[int[true]]
    def __init__(self:"FV", # type: Ref[FV[true]]
                elem:int,  # type: Ref[int[true]]
                ) -> "FV":
        # type: (...) -> Ref[FV[true]]
        super().__init__()
    
    def size(self: "FV", # type: Ref[FV[true]]
               ) -> int:
        # type: (...) -> Ref[int[true]]
        return 1
    def subst(self:"FV", # type: Ref[FV[true]]
             name:int, # type: Ref[int[true]]
             expr: Expr, # type: Ref[Expr[v.size() == 1]]
             ) -> "FV":
        # type: (...) -> Ref[Expr[v.size()==self.size()]]
        return expr
@interface
class Type:
    def __init__(self:"Type") -> "Type":
        pass
class Arrow(Type):
    t1 = None # type: Ref[Type[true]]
    t2 = None # type: Ref[Type[true]]
    def __init__(self: "Arrow", _t1:Type, _t2:Type) -> "Arrow":
        self.t1 = _t1
        self.t2 = _t2
        super().__init__()

class noType(Type):
    def __init__(self: Type) -> Type:
        super().__init__()
@interface
class Env:
    def __init__(self:"Env"
                 ) -> "Env":
        pass
    def contains(self:"Env", x:int) -> bool:
        pass
    def get(self:"Env", x:int) -> Type:
        pass
    def weaken(self:"Env", x:int, t:Type, 
               y:int, # type:Ref[int[not (y==x)]]
               ) -> bool:
        # type: (...) -> Ref[bool[self.contains(y)==Cons(x,t,self).contains(y)]]
        pass
class Cons(Env):
    var = None # type: Ref[int[true]]
    elem = None # type: Ref[Type[true]]
    next = None # type: Ref[Env[true]]
    def __init__(self:"Cons", var:int, elem:Type, next:"Env") -> "Cons":
        # type: (...) -> Ref[Cons[true]]
        super().__init__()
    
    def contains(self:"Cons", x:int) -> bool:
        return True if x == self.var else self.next.contains(x)
    
    def get(self:"Cons", x:int) -> Type:
        return self.elem if x == self.var else self.next.get(x)
    def weaken(self:"Cons", x:int, t:Type, 
               y:int, # type:Ref[int[not (y==x)]]
               ) -> bool:
        # type: (...) -> Ref[bool[self.contains(y)==Cons(x,t,self).contains(y)]]
        return True
class Nil(Env):
    def __init__(self:"Nil") -> "Nil":
        # type: (...) -> Ref[Nil[true]]
        pass
    
    def contains(self:"Nil", x:int) -> bool:
        return False
    
    def get(self:"Nil", x:int) -> Type:
        return noType()
    def weaken(self:"Env", x:int, t:Type, 
               y:int, # type:Ref[int[not (y==x)]]
               ) -> bool:
        # type: (...) -> Ref[bool[self.contains(y)==Cons(x,t,self).contains(y)]]
        return True
class HP:
    gamma = None # type: Ref[Env[true]]
    e = None # type: Ref[Expr[true]]
    tau = None # type: Ref[Type[true]]
    def __init__(self:"HP", _g:Env, _e:Expr, _tau:Type) -> "HP":
        pass
@interface
class HasType:
    def __init__(self:"HasType") -> "HasType":
        pass
    def fresh(self: "HasType", x:int) -> bool:
        pass
    def prop(self: "HasType") -> HP:
        pass
    @admitted
    def permutate(self:"HasType", x1: int,t1:Type,x2: int,t2:Type,g_:Env, e:Expr, 
                t:Type, # type: Ref[Type[self.prop() == HP(Cons(x2,t2,Cons(x1,t1,g_)),e,t)]]
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(Cons(x1,t1,Cons(x2,t2,g_)),e,t)]]
        pass
    def weaken(self:"HasType", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               x: int, # type: Ref[int[self.fresh(v)]]
               t2:Type
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(Cons(x, t2, g),e,t)]]
        pass
class TVar(HasType): 
    g:Env
    x = None # type: Ref[int[self.g.contains(v)]]
    def __init__(self: "TVar", g:Env, 
                 x:int # type: Ref[int[g.contains(v)]]
                 ) -> HasType:
        self.g = g
        self.x = x
        super().__init__()
    
    def fresh(self: "TVar", x:int) -> bool:
        return not (x == self.x)
    
    def prop(self: "TVar") -> HP:
        # type: (...) -> Ref[HP[v==HP(self.g, FV(self.x), self.g.get(self.x))]]
        return HP(self.g, FV(self.x), self.g.get(self.x))
    def weaken(self:"TVar", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               x: int, # type: Ref[int[self.fresh(v)]]
               t2:Type
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(Cons(x, t2, g),e,t)]]
        _ = self.x
        _ = self.g.weaken(x, t2, self.x)
        return TVar(Cons(x, t2, g), self.x)
class TAbs(HasType):
    g:Env
    x:int
    e:Expr
    t1:Type
    t2:Type
    te = None  # type: Ref[HasType[v.prop() == HP(Cons(self.x, self.t1, self.g), self.e, self.t2)]]
    def __init__(self: "TAbs", g:Env, x:int, e:Expr, t1:Type, t2:Type,
                 te: HasType, # type: Ref[HasType[v.prop() == HP(Cons(x, t1, g), e, t2)]]
                 ) -> "TAbs":
        self.g = g
        self.x = x
        self.e = e
        self.t1 = t1
        self.t2 = t2
        self.te = te
    
    def fresh(self: "TAbs", x:int) -> bool:
        return self.te.fresh(x)
    
    def prop(self: "TAbs") -> HP:
        return HP(self.g, Lambda(self.x, self.e), Arrow(self.t1, self.t2))
    # def permutate(self:"TAbs", x1: int,t1:Type,x2: int,t2:Type,g_:Env, e:Expr, 
    #         t:Type, # type: Ref[Type[self.prop() == HP(Cons(x2,t2,Cons(x1,t1,g_)),e,t)]]
    #         ) -> "HasType":
    #     # type: (...) -> Ref[HasType[v.prop() == HP(Cons(x1,t1,Cons(x2,t2,g_)),e,t)]]
    #     te = self.te # te.prop() = HP(Cons(self.x, self.t1, self.g), self.e, self.t2), self.g = Cons(x2,t2,Cons(x1,t1,g_))
    #     te1 = te.permutate(x1, t1, x2, t2, g_, self.e, self.t2) # Gives: To prove: te.prop() = HP(Cons(x2,t2,Cons(x1,t1,g_)),self.e,self.t2)
    #     return TAbs(Cons(x1,t1,Cons(x2,t2,g_)), self.x, self.e, self.t1, self.t2, te1) # To prove: te1.prop() = HP(Cons(self.x, self.t1, Cons(x1,t1,Cons(x2,t2,g_))), self.e, self.t2)
    #     # To prove: g = Cons(x1,t1,Cons(x2,t2,g_))
    def weaken(self:"TAbs", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               x: int, # type: Ref[int[self.fresh(v)]]
               t2:Type
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(Cons(x, t2, g),e,t)]]
        te = self.te
        te1 = te.weaken(Cons(self.x, self.t1, self.g),self.e, self.t2, x, t2)
        te2 = te1.permutate(self.x, self.t1, x, t2, self.g, self.e, self.t2)
        return TAbs(Cons(x, t2, g), self.x, self.e, self.t1, self.t2, te2)
class TApp(HasType):
    g:Env = None 
    e1:Expr = None
    e2:Expr = None 
    t1:Type = None 
    t2:Type = None 
    Te1 = None # type: Ref[HasType[v.prop() == HP(self.g,self.e1,Arrow(self.t1, self.t2))]]
    Te2 = None # type: Ref[HasType[v.prop() == HP(self.g,self.e2,self.t1)]]
    #
    def __init__(self:"TApp", _g:Env, _e1:Expr, _e2:Expr, _t1:Type, _t2:Type, 
                 te1:HasType, # type: Ref[HasType[v.prop() == HP(_g,_e1,Arrow(_t1, _t2))]]
                 te2:HasType, # type: Ref[HasType[v.prop() == HP(_g,_e2,_t1)]]
                 ) -> "TApp":
        self.e1 = _e1
        self.e2 = _e2
        self.t1 = _t1
        self.t2 = _t2
        self.g = _g
        self.Te1 = te1
        self.Te2 = te2
    
    def fresh(self: "TApp", x:int) -> bool:
        return self.Te1.fresh(x) and self.Te2.fresh(x)
    
    def prop(self: "TApp") -> HP:
        # type: (...) -> Ref[HP[v==HP(self.g, App(self.e1, self.e2), self.t2)]]
        gg = self.g
        ee1 = self.e1
        ee2 = self.e2
        tt2 = self.t2
        aa = App(ee1, ee2)
        
        return HP(gg, aa, tt2)
    
    def weaken(self:"TApp", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               x: int, # type: Ref[int[self.fresh(v)]]
               t2:Type
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(Cons(x, t2, g),e,t)]]
        Tee1 = self.Te1
        Tee2 = self.Te2
        tt = Arrow(self.t1, self.t2)
        Te1_ = self.Te1.weaken(self.g, self.e1, tt, x, t2)
        Te2_ = self.Te2.weaken(self.g, self.e2, self.t1, x, t2)

        return TApp(Cons(x, t2, self.g), self.e1, self.e2, self.t1, self.t2, Te1_, Te2_)
        

