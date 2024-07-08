@interface
class Expr:
    def __init__(self:"Expr") -> "Expr":
        pass
class Lambda(Expr):
    v = None # type: Ref[int[true]]
    body = None # type: Ref[Expr[true]]
    def __init__(self:"Lambda", elem:int, next:"Expr") -> "Lambda":
        super().__init__()
class App(Expr):
    e1 = None  # type: Ref[Expr[true]]
    e2 = None  # type: Ref[Expr[true]]
    def __init__(self: "App", _e1:Expr, _e2:Expr) -> "App":
        self.e1 = _e1
        self.e2 = _e2

class FV(Expr):
    v = None # type: Ref[int[true]]
    def __init__(self:"FV", # type: Ref[Lambda[true]]
                v:int,  # type: Ref[int[true]]
                ) -> "FV":
        # type: (...) -> Ref[Cons[true]]
        self.v = v
@interface
class MaybeType:
    def __init__(self:"MaybeType") -> "MaybeType":
        pass
class NoType(MaybeType):
    def __init__(self:"NoType") -> "NoType":
        pass
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

class OkType(MaybeType):
    t:Type
    def __init__(self:"OkType", t:Type) -> "OkType":
        self.t = t
@interface
class Env:
    def __init__(self:"Env" # type: Ref[List[true]]
                 ) -> "Env":
        # type: (...) -> Ref[List[true]]
        pass
    def get(self:"Env", x:int) -> MaybeType:
        pass
    def included(self: "Env", another: "Env") -> bool:
        pass
    def fresh(self: "Env", vv: int) -> bool:
        pass
    def fresh_enough(self: "Env") -> bool:
        pass
    def fresh_enough_def(self:"Env", x:int) -> bool:
        # type: (...) -> Ref[bool[self.fresh(x) if self.fresh_enough() else True]]
        pass
    def fresh_enough_extend(self:"Env", x:int, t:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).fresh_enough() if self.fresh_enough() else True]]
        pass
    
    def included_get(self:"Env", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int) -> bool:
        # type: (...) -> Ref[bool[True if self.get(x) == NoType() else self.get(x)==another.get(x)]]
        pass 
    def get_weaken(self:"Env", x:int, t:Type,
                    y:int, # type: Ref[int[not(v==x)]]
                    s:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).get(y)==OkType(s) if self.get(y) == OkType(s) else True]]
        pass
    def included_weaken(self:"Env", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int, # type: Ref[int[self.fresh(x)]]
                     t:Type) -> bool:
        # type: (...) -> Ref[bool[self.included(Cons(x,t,another))]]
        pass
    def map_extend_included(self:"Env", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int, # type: Ref[int[self.fresh(x)]]
                     t:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).included(Cons(x,t,another))]]
        pass
class Cons(Env):
    var = None # type: Ref[int[true]]
    elem = None # type: Ref[Type[true]]
    next = None # type: Ref[Env[true]]
    def __init__(self:"Cons", var:int, elem:Type, next:"Env") -> "Cons":
        # type: (...) -> Ref[Cons[true]]
        super().__init__()

    def fresh_enough(self: "Cons") -> bool:
        return True
    def fresh_enough_def(self:"Cons", x:int) -> bool:
        # type: (...) -> Ref[bool[self.fresh(x) if self.fresh_enough() else True]]
        pass
    def fresh_enough_extend(self:"Cons", x:int, t:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).fresh_enough() if self.fresh_enough() else True]]
        pass
    
    def get(self:"Cons", x:int) -> MaybeType:
        return OkType(self.elem) if x == self.var else self.next.get(x)
    
    def included(self: "Cons", another: "Env") -> bool:
        return another.get(self.var) == OkType(self.elem) and self.next.included(another) # another.get(self.var) == OkType(self.elem) and self.next.included(another)
    
    def included_get(self:"Cons", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int) -> bool:
        # type: (...) -> Ref[bool[True if self.get(x) == NoType() else self.get(x)==another.get(x)]]
        _ = self.next.included_get(another, x)
        # why must explicitly split here? 
        return True if x == self.var else True
        # return True
    
    
    def fresh(self: "Cons", vv: int) -> bool:
        return not (vv == self.var) and self.next.fresh(vv)
    
    def get_weaken(self:"Cons", x:int, t:Type, 
                   y:int, # type: Ref[int[not(v==x)]]
                   s:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).get(y)==OkType(s) if self.get(y) == OkType(s) else True]]
        return True
    
    def included_weaken(self:"Cons", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int, # type: Ref[int[self.fresh(x)]]
                     t:Type) -> bool:
        # type: (...) -> Ref[bool[self.included(Cons(x,t,another))]]
        _ = self.next.included_weaken(another, x, t)
        __ = another.get_weaken(x,t, self.var, self.elem)
        return True
    def map_extend_included(self:"Cons", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int, # type: Ref[int[self.fresh(x)]]
                     t:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).included(Cons(x,t,another))]]
        # Cons(x,t,self).included(Cons(x,t,another))
        _ = self.included_weaken(another, x, t)
        return True
class Nil(Env):
    def __init__(self: "Nil") -> "Nil":
        # type: (...) -> Ref[Nil[true]]
        pass
    def fresh_enough(self: "Nil") -> bool:
        return True
    @admitted
    def fresh_enough_def(self:"Nil", x:int) -> bool:
        # type: (...) -> Ref[bool[self.fresh(x) if self.fresh_enough() else True]]
        return True
    @admitted
    def fresh_enough_extend(self:"Nil", x:int, t:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).fresh_enough() if self.fresh_enough() else True]]
        return True
    
    def get(self:"Nil", x:int) -> MaybeType:
        return NoType()
    
    def included(self: "Nil", another: "Env") -> bool:
        return True
    def included_get(self:"Nil", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int) -> bool:
        # type: (...) -> Ref[bool[True if self.get(x) == NoType() else self.get(x)==another.get(x)]]
        return True
    
    
    def fresh(self: "Nil", vv: int) -> bool:
        return True
    
    def get_weaken(self:"Nil", x:int, t:Type, 
                   y:int, # type: Ref[int[not(v==x)]]
                   s:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).get(y)==OkType(s) if self.get(y) == OkType(s) else True]]
        return True
    def included_weaken(self:"Nil", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int, # type: Ref[int[self.fresh(x)]]
                     t:Type) -> bool:
        # type: (...) -> Ref[bool[self.included(Cons(x,t,another))]]
        return True
    def map_extend_included(self:"Nil", 
                     another: "Env", # type: Ref[Env[self.included(v)]]
                     x:int, # type: Ref[int[self.fresh(x)]]
                     t:Type) -> bool:
        # type: (...) -> Ref[bool[Cons(x,t,self).included(Cons(x,t,another))]]
        _ = self.included_weaken(another, x, t)
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
    def prop(self: "HasType") -> HP:
        pass
    def typing_weakening(self:"HasType", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
                g_:Env, #type: Ref[Env[g.included(v) and v.fresh_enough()]]
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(g_,e,t)]]
        pass
class TVar(HasType): 
    g:Env
    x:int
    t = None # type: Ref[Type[self.g.get(self.x)==OkType(v)]]
    def __init__(self: "TVar", g:Env, 
                 x:int, 
                 t:Type # type: Ref[Type[g.get(x)==OkType(v)]]
                 ) -> HasType:
        self.g = g
        self.x = x
        self.t = t
    
    def prop(self: "TVar") -> HP:
        # type: (...) -> Ref[HP[v==HP(self.g, FV(self.x), self.t)]]
        return HP(self.g, FV(self.x), self.t)
    def typing_weakening(self:"TVar", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               g_:Env, #type: Ref[Env[g.included(v) and v.fresh_enough()]]
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(g_, e,t)]]
        _ = self.t
        # __ = self.g.included_get(g_, self.x) 
        return TVar(g_, self.x, self.t) # proof error: forget a lemma (Line 235)
class TAbs(HasType):
    g:Env
    x = None # type: Ref[int[self.g.fresh(v)]]
    e:Expr
    t1:Type
    t2:Type
    te = None  # type: Ref[HasType[v.prop() == HP(Cons(self.x, self.t1, self.g), self.e, self.t2)]]
    def __init__(self: "TAbs", g:Env, 
                 x:int, # type: Ref[int[g.fresh(x)]]
                 e:Expr, t1:Type, t2:Type,
                 te: HasType, # type: Ref[HasType[v.prop() == HP(Cons(x, t1, g), e, t2)]]
                 ) -> "TAbs":
        self.g = g
        self.x = x
        self.e = e
        self.t1 = t1
        self.t2 = t2
        self.te = te
    
    def prop(self: "TAbs") -> HP:
        return HP(self.g, Lambda(self.x, self.e), Arrow(self.t1, self.t2))
    def typing_weakening(self:"TAbs", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               g_:Env, #type: Ref[Env[g.included(v) and v.fresh_enough()]]
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(g_,e,t)]]
        xx = self.x
        te = self.te
        ___ = g_.fresh_enough_def(self.x)
        ____ = g_.fresh_enough_extend(self.x, self.t1)
        _ = self.g.map_extend_included(g_, self.x, self.t1)
        te1 = te.typing_weakening(Cons(self.x, self.t1, self.g),self.e, self.t2, Cons(self.x, self.t1, g_))
        return TAbs(g_, self.x, self.e, self.t1, self.t2, te1)
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
    
    def prop(self: "TApp") -> HP:
        # type: (...) -> Ref[HP[v==HP(self.g, App(self.e1, self.e2), self.t2)]]
        gg = self.g
        ee1 = self.e1
        ee2 = self.e1 
        tt2 = self.t2
        aa = App(ee1, ee2) 
        
        return HP(gg, aa, tt2) # programming error: wrong variable used (should be self.e1)
    
    def typing_weakening(self:"TApp", g:Env, e:Expr, 
               t:Type, # type: Ref[Type[self.prop() == HP(g,e,t)]]
               g_:Env, #type: Ref[Env[g.included(v) and v.fresh_enough()]]
               ) -> "HasType":
        # type: (...) -> Ref[HasType[v.prop() == HP(g_,e,t)]]
        Tee1 = self.Te1
        Tee2 = self.Te2
        tt = Arrow(self.t1, self.t2)
        Te1_ = self.Te1.typing_weakening(self.g, self.e1, tt, g_)
        Te2_ = self.Te2.typing_weakening(self.g, self.e2, self.t1, g_)

        return TApp(g_, self.e1, self.e2, self.t1, self.t2, Te1_, Te2_)
        

