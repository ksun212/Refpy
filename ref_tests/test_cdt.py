from typing import cast

def D__Cast(x:object) -> "D":
    pass


def D__Inst(x:object) -> "bool":
    pass

class C:
    f1 = 0 
    def __init__(self:"C") -> "C":
        pass

class D(C):
    f2 = 0 # type: Ref[int[v==1]]
    def __init__(self:"D") -> "D":
        super().__init__()

    def f(self:"D", 
          x:"C" # type: Ref[int[v.f1==1]]
          ) -> int:
        # type: (...) -> Ref[int[v>0]]
        return D__Cast(x).f2 if D__Inst(x) else x.f1