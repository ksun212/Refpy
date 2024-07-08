@interface
class Peano:
    def __init__(self:"Peano") -> "Peano":
        pass
    def plus(self:"Peano", ano:"Peano") -> "Peano":
        pass
    def zeroL(self: "Peano", 
              ano:"Peano" # type: Ref[Peano[v==Z()]]
              ) -> bool:
        # type: (...) -> Ref[bool[ano.plus(self)==self]]
        pass
    def zeroR(self: "Peano", 
              ano:"Peano" # type: Ref[Peano[v==Z()]]
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(ano)==self]]
        pass
    def succR(self: "Peano", 
              ano:"Peano" 
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(S(ano))==S(self.plus(ano))]]
        pass
    def comm(self: "Peano", 
              ano:"Peano" 
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(ano)==ano.plus(self)]]
        pass
class Z(Peano):
    def __init__(self:"Z") -> "Z":
        pass
    
    def plus(self:"Z", ano:Peano) -> Peano:
        return ano
    def generatedness(self: "Z") -> bool:
        # type: (...) -> Ref[bool[self==Z()]]
        pass
    def zeroL(self: "Z", 
              ano:"Peano" # type: Ref[Peano[v==Z()]]
              ) -> bool:
        # type: (...) -> Ref[bool[ano.plus(self)==self]]
        return True
    def zeroR(self: "Z", 
              ano:"Peano" # type: Ref[Peano[v==Z()]]
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(ano)==self]]
        # _ = self.generatedness()
        return True
    def succR(self: "Z", 
              ano:"Peano" 
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(S(ano))==S(self.plus(ano))]]
        # _ = self.generatedness()
        return True
    def comm(self: "Z", 
              ano:"Peano" 
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(ano)==ano.plus(self)]]
        # __ = self.generatedness()
        _ = ano.zeroR(self)
        return True
class S(Peano):
    pred: Peano
    def __init__(self:"S", pred:Peano) -> "S":
        pass
    
    def plus(self:"S", ano:Peano) -> Peano:
        return S(self.pred.plus(ano))
    def generatedness(self: "S") -> bool:
        # type: (...) -> Ref[bool[self==S(self.pred)]]
        pass
    def zeroL(self: "S", 
              ano:"Peano" # type: Ref[Peano[v==Z()]]
              ) -> bool:
        # type: (...) -> Ref[bool[ano.plus(self)==self]]
        return True
    
    def zeroR(self: "S", 
              ano:"Peano" # type: Ref[Peano[v==Z()]]
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(ano)==self]]
        # __ = self.generatedness()
        _ = self.pred.zeroR(ano)
        return True
    def succR(self: "S", 
              ano:"Peano" 
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(S(ano))==S(self.plus(ano))]]
        # _ = self.generatedness()
        __ = self.pred.succR(ano)
        return True
    def comm(self: "S", 
              ano:"Peano" 
              ) -> bool:
        # type: (...) -> Ref[bool[self.plus(ano)==ano.plus(self)]]
        # __ = self.generatedness()
        _ = ano.succR(self.pred)
        ___ = self.pred.comm(ano)
        return True