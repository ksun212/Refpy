@interface
class Pizza:
    def __init__(self: "Pizza") -> "Pizza":
        pass
    def remA(self: "Pizza") -> "Pizza":
        pass
    def noA(self: "Pizza") -> bool:
        pass
    def price(self:"Pizza") -> int:
        # type: (...) -> Ref[int[v>0]]
        pass
    def remA_idempotent(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.remA().remA() == self.remA()]]
        pass
    def remA_noA(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.remA().noA()]]
        pass
    def remA_noinc_price(self: "Pizza") -> bool:
        # type: (...) -> Ref[bool[self.price()>=self.remA().price()]]
        pass
    