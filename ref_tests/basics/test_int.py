
# def asserts(x:bool, # type: Ref[bool[Prop(v)]] 
#             ) -> int:
#     # type: (...) -> Ref[int[true]]
#     pass

# def eq(x:int, # type: Ref[int[true]]
#        y:int # type: Ref[int[true]]
#      ) -> bool:
#     # type: (...) -> Ref[bool[iff(Prop(v), x==y)]]
#     pass

# def twice(x:int, # type: Ref[int[true]]
#        y:int # type: Ref[int[true]]
#      ) -> bool:
#     # type: (...) -> Ref[bool[iff(Prop(v), v== 2 * x)]]
#     pass
def add(x: int, # type: Ref[int[true]]
       y:int # type: Ref[int[v == x]]
        ) -> int:
    # type: (...) -> Ref[int[v==y + x]]
    pass
def addboth(x:int,  # type: Ref[int[infer]]
            y:int,  # type: Ref[int[infer]]
         ) -> int:
    # type: (...) -> Ref[int[infer]]
    x_y = add(x, y)
    return x_y

# a = addboth(2, 2)
# b = add(a, 4)
# def add1(x:int,  # type: Ref[int[infer]]
#          ) -> int:
#     # type: (...) -> Ref[int[infer]]
#     one = 1
#     x_one = add(one, x)
#     return x_one
# def add2(x:int # type: Ref[int[infer]]
#          ) -> int:
#     # type: (...) -> Ref[int[v == x + 1]]
#     x_one = add1(x)
#     # ret = add(x_one, one)
#     return x_one
# def r3() -> int:
#     # type: (...) -> Ref[int[v==3]]
#     return 3
# a = 1
# # b = add(a,a)
# c = twice(1,1)
# d = asserts(c)