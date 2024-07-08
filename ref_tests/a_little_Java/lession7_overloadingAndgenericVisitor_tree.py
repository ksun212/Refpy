@interface
class Fruit:
    def __init__(self:"Fruit") -> "Fruit":
        pass
class Apple(Fruit):
    def __init__(self: "Apple") -> "Apple":
        pass
class Peach(Fruit):
    def __init__(self: "Peach") -> "Peach":
        pass
@interface
class Tree:
    def __init__(self: "Tree") -> "Tree":
        pass
    def accept(self:"Tree", ask:"bTreeVisitor") -> bool:
        pass
    def accepti(self:"Tree", ask:"iTreeVisitor") -> int:
        pass
    def height_ge_root(self:"Tree", hFn:"iHeight") -> bool:
        # type: (...) -> Ref[bool[self.accepti(hFn)>=hFn.root]]
        pass
@interface
class bTreeVisitor:
    def __init__(self:"bTreeVisitor") -> "bTreeVisitor":
        pass
    def forBud(self:"bTreeVisitor") -> bool:
        pass
    def forFlat(self:"bTreeVisitor", f:Fruit, t:Tree) -> bool:
        pass
    def forSplit(self:"bTreeVisitor", l:Tree, r:Tree) -> bool:
        pass
@interface
class iTreeVisitor:
    def __init__(self:"iTreeVisitor") -> "iTreeVisitor":
        pass
    def forBud(self:"iTreeVisitor") -> int:
        pass
    def forFlat(self:"iTreeVisitor", f:Fruit, t:Tree) -> int:
        pass
    def forSplit(self:"iTreeVisitor", l:Tree, r:Tree) -> int:
        pass
class iHeight(iTreeVisitor):
    root:int
    def __init__(self: "iHeight", root:int) -> "iHeight":
        self.root = root
    
    def forBud(self:"iHeight") -> int:
        return self.root
    
    def forFlat(self:"iHeight", f:Fruit, t:Tree) -> int:
        return t.accepti(self) + 1
    
    def forSplit(self:"iHeight", l:Tree, r:Tree) -> int:
        return l.accepti(self) + 1 # no max yet. 
class bIsFlat(bTreeVisitor):
    def __init__(self: "bIsFlat") -> "bIsFlat":
        pass
    
    def forBud(self:"bIsFlat") -> bool:
        return True
    
    def forFlat(self:"bIsFlat", f:Fruit, t:Tree) -> bool:
        return t.accept(self)
    
    def forSplit(self:"bIsFlat", l:Tree, r:Tree) -> bool:
        return False
class bIsSplit(bTreeVisitor):
    def __init__(self: "bIsSplit") -> "bIsSplit":
        pass
    
    def forBud(self:"bIsSplit") -> bool:
        return True
    
    def forFlat(self:"bIsSplit", f:Fruit, t:Tree) -> bool:
        return False
    
    def forSplit(self:"bIsSplit", l:Tree, r:Tree) -> bool:
        return r.accept(self) if l.accept(self) else False

class Bud(Tree):
    def __init__(self: "Bud") -> "Bud":
        pass
    
    def accept(self:"Bud", ask:bTreeVisitor) -> bool:
        return ask.forBud()
    
    def accepti(self:"Bud", ask:"iTreeVisitor") -> int:
        return ask.forBud()
    def height_ge_root(self:"Bud", hFn:"iHeight") -> bool:
        # type: (...) -> Ref[bool[self.accepti(hFn)>=hFn.root]]
        return True
class Flat(Tree):
    f:Fruit
    t: Tree
    def __init__(self: "Flat", f:Fruit, t:Tree) -> "Flat":
        self.f = f
        self.t = t
    
    def accept(self: "Flat", ask:bTreeVisitor) -> bool:
        return ask.forFlat(self.f, self.t)
    
    def accepti(self:"Flat", ask:"iTreeVisitor") -> int:
        return ask.forFlat(self.f, self.t)
    def height_ge_root(self:"Flat", hFn:"iHeight") -> bool:
        # type: (...) -> Ref[bool[self.accepti(hFn)>=hFn.root]]
        _ = self.t.height_ge_root(hFn)
        return True
class Split(Tree):
    l:Tree
    r:Tree
    def __init__(self: "Split", l:Tree, r:Tree) -> "Split":
        self.l = l
        self.r = r
    
    def accept(self: "Split", ask:bTreeVisitor) -> bool:
        return ask.forSplit(self.l, self.r)
    
    def accepti(self:"Split", ask:"iTreeVisitor") -> int:
        return ask.forSplit(self.l, self.r)
    def height_ge_root(self:"Split", hFn:"iHeight") -> bool:
        # type: (...) -> Ref[bool[self.accepti(hFn)>=hFn.root]]
        _ = self.l.height_ge_root(hFn)
        return True
class Main:
    def __init__(self:"Main") -> "Main":
        pass
    def assertTrue(self:"Main", 
                     b: bool, # type: Ref[Pie[v==true]]
                     )->bool:
        return True
    def assertFalse(self:"Main", 
                     b: bool, # type: Ref[Pie[v==False]]
                     )->bool:
        return True
    def assertEqn(self:"Main", x:int,
                     y: int, # type: Ref[int[v==x]]
                     )->bool:
        return True
    
    def test(self:"Main") -> bool:
        p = Flat(Apple(), Bud())
        b = p.accept(bIsFlat())
        _ = self.assertTrue(b)
        return True
    def test2(self:"Main") -> bool:
        p = Split(Bud(), Bud())
        b = p.accept(bIsSplit())
        _ = self.assertTrue(b)
        return True
    def test3(self:"Main") -> bool:
        p = Split(Bud(), Bud())
        n = p.accepti(iHeight(0))
        _ = self.assertEqn(n, 1)
        return True
    