# from typing import Final
# class C:
#     xxx:Final[int]
#     def __init__(self:"C", # type: Ref[C[true]]
#                  x:int = 1 # type: Ref[int[v>0]]
#                  ) -> "C":
#         # type: (...) -> Ref[C[v.xxx==x]]
#         self.xxx = x
#     def x_add_one(self:"C",  # type: Ref[C[true]]
#                   one:int = 1 # type: Ref[int[v>0]]
#                   ) -> int:
#         # type: (...) -> Ref[int[v == self.xxx]]
#         x = self.xxx
#         return x
# aa = C(2)
# b = aa.x_add_one(3)
def f(x:int = 3, # type: Ref[int[v>2]]
      y: int = 2 # type: Ref[int[v>0]]
      ) -> int:
    # type: (...) -> Ref[int[v>0]]
    return 1

a = f(y = 1)