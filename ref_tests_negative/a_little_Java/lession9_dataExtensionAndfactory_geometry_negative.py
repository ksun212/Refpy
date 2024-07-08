# since we do not support sqrt currently, we stick to ManhattanPt. 
# class Point:
#     x:int
#     y:int
#     # def __init__(self: "Point", x:int, y:int) -> "Point":
#     #     self.x = x
#     #     self.y = y
class ManhattanPt:
    x = None # type: Ref[int[v>=0]]
    y = None # type: Ref[int[v>=0]]
    def __init__(self: "ManhattanPt", _x: int, _y: int) -> "ManhattanPt":
        self.x = _x
        self.y = _y
    
    def distanceToO(self: "ManhattanPt") -> int:
        # type: (...) -> Ref[int[v==self.x + self.y]]
        xx = self.x
        yy = self.y
        return xx + yy
    
    def closerToO(self: "ManhattanPt", p: "ManhattanPt") -> bool:
        return p.distanceToO() >= self.distanceToO()
    
    def minus(self: "ManhattanPt", p: "ManhattanPt") -> "ManhattanPt":
        return ManhattanPt(self.x-p.x, self.y-p.y)
    
    def plus(self: "ManhattanPt", p: "ManhattanPt") -> "ManhattanPt":
        return ManhattanPt(self.x+p.x, self.y+p.y)
    # need destruct 
    # def plus_mins(self: "ManhattanPt", p: "ManhattanPt", q: "ManhattanPt") -> bool:
    #     # type: (...) -> Ref[bool[self==q.minus(p) if self.plus(p)==q else True]]
    #     # self == ManhattanPt(q.x-p.x, q.y-p.y) => ManhattanPt(self.x+p.x, self.y+p.y) == q
    #     return True

    # def plus_mins_destruct(self: "ManhattanPt", p: "ManhattanPt", q: "ManhattanPt", qx1:int, qy1:int, qx2:int, qy2:int) -> bool:
    #     # type: (...) -> Ref[bool[self==q.minus(p) if self == ManhattanPt(qx1, qy1) and q == ManhattanPt(qx2, qy2) and self.plus(p)==q else True]]
    #     # self == ManhattanPt(q.x-p.x, q.y-p.y) => ManhattanPt(self.x+p.x, self.y+p.y) == q
    #     return True
# invok super not supported, the override is too strong too. 
# class ShadowedManhattanPt
@interface
class Shape:
    def __init__(self:"Shape") -> "Shape":
        pass
    def accept(self:"Shape", ask:"ShapeVisitor") -> bool:
        pass
    def O(self:"Shape") -> ManhattanPt:
        pass
    def origin_in_shape(self:"Shape", haspt: "HasPtV") -> bool:
        # type: (...) -> Ref[bool[self.accept(haspt) == True if self.O() == haspt.p else True]]
        pass
@interface
class ShapeVisitor:
    def __init__(self:"ShapeVisitor") -> "ShapeVisitor":
        pass
    def forCircle(self:"ShapeVisitor", r:int) -> bool:
        pass
    def forSquare(self:"ShapeVisitor", s:int) -> bool:
        pass
    def forTrans(self:"ShapeVisitor", p:ManhattanPt, s:Shape) -> bool:
        pass
    def forUnion(self: "ShapeVisitor", s:Shape, t:Shape) -> bool:
        pass

class HasPtV(ShapeVisitor):
    p:ManhattanPt
    def __init__(self:"HasPtV", p:ManhattanPt) -> "HasPtV":
        self.p = p
    
    def newHasPt(self:"HasPtV", p:ManhattanPt) -> "HasPtV":
        return HasPtV(p)
    
    def forCircle(self:"HasPtV", r:int) -> bool:
        return r >= self.p.distanceToO()
    
    def forSquare(self:"HasPtV", s:int) -> bool:
        return s >= self.p.x and s >= self.p.y
    
    def forTrans(self:"HasPtV", p:ManhattanPt, s:Shape) -> bool:
        # a = HasPtV(ManhattanPt(0, 0))
        return s.accept(self.newHasPt(self.p.minus(p))) # 
    
    def forUnion(self: "HasPtV", s:Shape, t:Shape) -> bool:
        return True if s.accept(self) else t.accept(self) 
    # 
# we can not support extension, it violates type constraints. 
# class UnionHasPtV(HasPtV):
#     def __init__(self: "UnionHasPtV", p: ManhattanPt) -> "UnionHasPtV":
#         super().__init__(p)
#     def newHasPt(self:"UnionHasPtV", p:ManhattanPt) -> "ShapeVisitor":
#         return UnionHasPtV(p)
#     
#     def forUnion(self: "UnionHasPtV", s:Shape, t:Shape) -> bool:
#         return True if s.accept(self) else t.accept(self) 
class Circle(Shape):
    r = None # type: Ref[int[v>=0]]
    def __init__(self:"Circle", r:int) -> "Circle":
        self.r = r
    
    def accept(self:"Circle", ask:ShapeVisitor) -> bool:
        return ask.forCircle(self.r)
    
    def O(self:"Circle") -> ManhattanPt:
        return ManhattanPt(0,0)
    def origin_in_shape(self:"Circle", haspt: "HasPtV") -> bool:
        # type: (...) -> Ref[bool[self.accept(haspt) == True if self.O() == haspt.p else True]]
        _ = self.r
        return True
class Square(Shape):
    s = None # type: Ref[int[v>=0]]
    def __init__(self:"Square", s:int) -> "Square":
        self.s = s
    
    def accept(self:"Square", ask:ShapeVisitor) -> bool:
        return ask.forSquare(self.s)
    
    def O(self:"Square") -> ManhattanPt:
        return ManhattanPt(0,0)
    def origin_in_shape(self:"Square", haspt: "HasPtV") -> bool:
        # type: (...) -> Ref[bool[self.accept(haspt) == True if self.O() == haspt.p else True]]
        _ = self.s
        return True
class Trans(Shape):
    p:ManhattanPt
    s:Shape
    def __init__(self:"Trans", p:ManhattanPt, s:Shape) -> "Trans":
        self.p = p
        self.s = s
    
    def accept(self:"Trans", ask:ShapeVisitor) -> bool:
        return ask.forTrans(self.p, self.s)
    
    def O(self:"Trans") -> ManhattanPt:
        return self.s.O().plus(self.p)
    def origin_in_shape(self:"Trans", haspt: "HasPtV") -> bool:
        # type: (...) -> Ref[bool[self.accept(haspt) == True if self.O() == haspt.p else True]]
        # _ = self.s.origin_in_shape(haspt.newHasPt(haspt.p.minus(self.p))) 
        # __ = self.s.O().plus_mins(self.p, haspt.p)
        return True # proof error: forget an induction hyphothesis (Line 137)
        # self.s.accept(haspt.newHasPt(haspt.p.minus(self.p))) == True if self.s.O() == haspt.newHasPt(haspt.p.minus(self.p)).p === haspt.p.minus(self.p)
        # self.s.accept(HasPtV(haspt.p.minus(self.p))) == True if (self.O() == haspt.p === self.s.O().plus(self.p)== haspt.p)
class Union(Shape):
    s:Shape
    t:Shape
    
    def __init__(self:"Union", s:Shape, t:Shape) -> "Union":
        self.s = s
        self.t = t
    
    def accept(self:"Union", ask:ShapeVisitor) -> bool:
        return ask.forUnion(self.s, self.t)
    
    def O(self:"Union") -> ManhattanPt:
        return self.s.O()
    def origin_in_shape(self:"Union", haspt: "HasPtV") -> bool:
        # type: (...) -> Ref[bool[self.accept(haspt) == True if self.O() == haspt.p else True]]
        _ = self.s.origin_in_shape(haspt) 
        # __ = self.t.origin_in_shape(haspt) 
        
        # True if self.s.accept(haspt) else self.t.accept(haspt) 
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
    
    def test(self:"Main") -> bool:
        p = Circle(10)
        p2 = p.accept(HasPtV(ManhattanPt(4,4)))
        _ = self.assertTrue(p2)
        return True

    def test2(self:"Main") -> bool:
        p = Trans(ManhattanPt(1,1), Circle(10))
        p2 = p.accept(HasPtV(ManhattanPt(10,10)))
        _ = self.assertTrue(p2) # programming error: the point is not in the shape
        return True
    def test3(self:"Main") -> bool:
        p = Union(Circle(10), Trans(ManhattanPt(1,1), Circle(10)))
        p2 = p.accept(HasPtV(ManhattanPt(6,6)))
        _ = self.assertTrue(p2)
        return True
    
    
    