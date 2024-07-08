@interface
class Point:
    def __init__(self: "Point") -> "Point":
        pass
class ManhattanPt(Point):
    x = None # type: Ref[int[true]]
    y = None # type: Ref[int[true]]
    
    def __init__(self: "ManhattanPt", _x: int, _y: int) -> "ManhattanPt":
        self.x = _x
        self.y = _y
    def distanceToO(self: "ManhattanPt") -> int:
        # type: (...) -> Ref[int[v==self.x + self.y]]
        xx = self.x
        yy = self.y
        return xx + yy