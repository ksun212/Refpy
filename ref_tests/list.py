
@interface
class List:
    def __init__(self:"List" # type: Ref[List[true]]
                 ) -> "List":
        # type: (...) -> Ref[List[true]]
        pass
    def length(self:"List", # type: Ref[List[true]]
                )->int:
        # type: (...) -> Ref[int[true]] 
        pass
    def contains(self:"List", x:int) -> bool:
        pass
    def sorted(self: "List") -> bool:
        pass
    def getHead(self: "List") -> int:
        pass
    def insert(self:"List", 
               x:int, # type: Ref[int[10000>=x]]
               ) -> "List":
        pass
    # def lem_insert(self:"List", 
    #                 y:int, # type: Ref[int[Cons(v, self).sorted()]]
    #                 x:int, # type: Ref[int[not (y>=x)]]
    #                 ) -> bool:
    #     # type: (...) -> Ref[bool[self.insert(x).getHead()>=y]]
    #     pass 
    def inserts_preserve_sortedness(self:"List", # type: Ref[List[v.sorted()]]
               x:int, # type: Ref[int[10000>=x]]
               ) -> "bool":
        # type: (...) -> Ref[bool[self.insert(x).sorted()]] 
        pass
    def contains_weakening(self:"List", x:int,
               y:int, # type:Ref[int[true]]
               ) -> bool:
        # type: (...) -> Ref[bool[Cons(x,self).contains(y) if self.contains(y) else True]]
        pass
class Cons(List):
    elem = None # type: Ref[int[true]]
    next = None # type: Ref[List[true]]
    def __init__(self:"Cons", elem:int, next:"List",  
                ) -> "Cons":
        super().__init__()

    def assertGt(self:"Cons", x:int, 
             y:int, # type: Ref[bool[x>=v]] 
            ) -> bool:
        # type: (...) -> Ref[bool[true]]
        return True
    
    def length(self: "Cons", # type: Ref[Cons[true]]
               ) -> int:
        # type: (...) -> Ref[int[true]]
        n = self.next
        l = n.length()
        return 1 + l
    
    def getHead(self: "Cons") -> int:
        return self.elem
    
    def sorted(self: "Cons") -> bool:
        return self.next.sorted() and self.next.getHead() >= self.elem
    
    def contains(self:"Cons", x:int) -> bool:
        return True if x == self.elem else self.next.contains(x)
    
    def insert(self:"Cons", 
               x:int, # type: Ref[int[10000>=x]]
               ) -> "Cons":
        return Cons(x, self) if self.elem >= x else Cons(self.elem, self.next.insert(x))
    # def lem_insert(self:"Cons", 
    #                 y:int, # type: Ref[int[Cons(v, self).sorted()]]
    #                 x:int, # type: Ref[int[not (y>=v)]]
    #                 ) -> bool:
    #     # type: (...) -> Ref[bool[self.insert(x).getHead()>=y]]
    #     return True
    def inserts_preserve_sortedness(self:"Cons", # type: Ref[Cons[v.sorted()]]
               x:int, # type: Ref[int[10000>=x]]
               ) -> "bool":
        # type: (...) -> Ref[bool[self.insert(x).sorted()]] 
        # not (self.elem >= x) => self.next.insert(x).getHead() >= self.elem
        _ = self.next.inserts_preserve_sortedness(x) # self.next.insert(x).sorted()
        return True
        # return True if self.elem >= x else True # self.next.lem_insert(self.elem, x) # Cons(x, self).sorted() == self.sorted() and self.getHead() >= x
    def contains_weakening(self:"Cons", x:int,
               y:int, # type:Ref[int[true]]
               ) -> bool:
        # type: (...) -> Ref[bool[Cons(x,self).contains(y) if self.contains(y) else True]]
        return True
class Nil(List):
    def __init__(self:"Nil") -> "Nil":
        pass
    
    def length(self: "Nil") -> int:
        return 0
    
    def getHead(self: "Nil") -> int:
        return 10000
    
    def sorted(self: "Nil") -> bool:
        return True
    
    def contains(self:"Nil", x:int) -> bool:
        return False
    
    def insert(self:"Nil",
               x:int, # type: Ref[int[10000>=x]]
               ) -> "List":
        return Cons(x, self)
    
    # def lem_insert(self:"Nil", 
    #             y:int, # type: Ref[int[Cons(v, self).sorted()]]
    #             x:int, # type: Ref[int[not (y>=x)]]
    #             ) -> bool:
    #     # type: (...) -> Ref[bool[self.insert(x).getHead()>=y]]
    #     return True
    
    def inserts_preserve_sortedness(self:"Nil", # type: Ref[List[v.sorted()]]
               x:int, # type: Ref[int[10000>=x]]
               ) -> "bool":
        # type: (...) -> Ref[bool[self.insert(x).sorted()]] 
        return True
    def contains_weakening(self:"Nil", x:int,
               y:int, # type:Ref[int[true]]
               ) -> bool:
        # type: (...) -> Ref[bool[Cons(x,self).contains(y) if self.contains(y) else True]]
        return True