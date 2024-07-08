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
def fun1(x: int, # type: Ref[int[true]]
        ) -> int:
    # type: (...) -> Ref[int[v>x+1]]
    pass

def fun2(x: int, # type: Ref[int[true]]
        ) -> int:
    # type: (...) -> Ref[int[v==x+1]]
    pass

class C:
    f1 = None # type: Ref[int[true]]
    f2 = None # type: Ref[int[v>self.f1]]
    def __init__(self:"C", # type: Ref[C[true]]
                 x:int = 1 # type: Ref[int[infer]]
                 ) -> "C":
        # type: (...) -> Ref[C[infer]]
        self.xxx = x
    # def x_add_one(self:"C"  # type: Ref[C[true]]
    #               ) -> int:
    #     # type: (...) -> Ref[int[v == self.xxx + 2]]
    #     one = 2
    #     x = self.xxx
    #     return add(x, one)
a = 1
C(fun2(a), fun1(1))

# aa = C(1)
# z = aa.x_add_one()
# c = add(1, z)
# class A:
#     x:Final[C]
#     def __init__(self: "A", # type: Ref[A[true]]
#                  x:int  # type: Ref[int[infer]]
#                  ) -> "A":
#         # type: (...) -> Ref[A[infer]]
#         self.x = C(x)

# # # c = C(1)
# # # one = c.xxx
# # # o = assert1(one)

# a = A(1)
# c = a.x
# one = c.xxx
# o = assert1(one)
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