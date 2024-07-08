from typing import Final
# def add(x: int, # type: Ref[int[true]]
#        y:int # type: Ref[int[v > 1]]
#         ) -> int:
#     # type: (...) -> Ref[int[v==x+y]]
#     pass
def assert1(x: int, # type: Ref[int[v == 1]]
        ) -> int:
    # type: (...) -> Ref[int[v==1]]
    pass
def assert2(x: int, # type: Ref[int[v == 2]]
        ) -> int:
    # type: (...) -> Ref[int[v==1]]
    pass
class C:
    xxx = None # type: Ref[int[v==1]]
    yyy = None # type: Ref[int[v>self.xxx]]
    
    def __init__(self:"C", # type: Ref[C[true]]
                 x:int, # type: Ref[int[v==1]]
                 y: int, # type: Ref[int[v>x]]
                 ) -> "C":
        # type: (...) -> Ref[C[true]]
        self.xxx = x
        self.yyy = y
    
    def ok(self:"C"  # type: Ref[C[true]]
                  ) -> int:
        # type: (...) -> Ref[int[v==1]]
        return 1
    def essential(self:"C"  # type: Ref[C[true]]
                  ) -> int:
        # type: (...) -> Ref[int[v == self.ok()]]
        # zz = self.ok()
        # ft = 42
        # tem1 = self.ok()
        return 1
    
aa = C(1, 2)
bb = aa.yyy
c = assert2(bb) 

# z = aa.x_add_one()
# c = add(1, z)
# class D(C):
#     def __init__(self: "D", # type: Ref[A[true]]
#                  x:int  # type: Ref[int[true]]
#                  ) -> "D":
#         # type: (...) -> Ref[A[true]]
#         # super().__init__(x)
#         pass
#     def essential_gt0(self: "D" # type: Ref[D[v.essential()]]
#                      ) -> bool: # Ref[bool[v]]
#         zz = self.xxx
#         ft = 42
#         return zz == ft

# def test_field_chain_function(x: C, # type: Ref[C[true]]
#                               ) -> A: 
#     # type: (...) -> Ref[A[v.x.xxx==x.xxx]]
#     c1 = x.xxx
#     r = A(c1)
#     return r
# def asserts(x1:bool, # type: Ref[bool[Prop(v)]]
#             ) -> int:
#     # type: (...) -> Ref[int[true]]
#     pass
# def eq(x2:int, # type: Ref[int[true]]
#        y2:int # type: Ref[int[true]]
#      ) -> bool:
#     # type: (...) -> Ref[bool[iff(Prop(v), x2==y2)]]
#     pass
# two = 2
# aa = C()
# z = aa.x
# a = z.x_add_one()
# b = 3
# c = eq(a,b)
# d = asserts(c)