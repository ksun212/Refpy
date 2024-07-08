

from __future__ import annotations

import sys
from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generic,
    Iterable,
    NamedTuple,
    NewType,
    Sequence,
    TypeVar,
    Union,
    cast,
)
from typing_extensions import Final, Self, TypeAlias as _TypeAlias, TypeGuard, overload

import refpy.nodes
from refpy.nodes import (
    ARG_POS,
    ARG_STAR,
    ARG_STAR2,
    ArgKind,
    Expression,
    FuncDef,
    SymbolNode,
)
from refpy.options import Options

T = TypeVar("T")
LiteralValue: _TypeAlias = Union[int, str, bool, float]


class TypeOfAny:
    __slots__ = ()
    explicit: Final = 2
    implicit: Final = 6


class Type(refpy.nodes.Context):
    
    def __init__(self, line: int = -1, column: int = -1) -> None:
        super().__init__(line, column)

    def accept(self, visitor: TypeVisitor[T]) -> T:
        raise RuntimeError("Not implemented")

    def __repr__(self) -> str:
        return self.accept(TypeStrVisitor(options=Options()))

class AnyType(Type):
    

    __slots__ = ("type_of_any")

    def __init__(
        self,
        type_of_any: int,
        line: int = -1,
        column: int = -1,
    ) -> None:
        super().__init__(line, column)
        self.type_of_any = type_of_any
    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_any(self)

    def __hash__(self) -> int:
        return hash(AnyType)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, AnyType)


class NoneType(Type):
    

    __slots__ = ()

    def __init__(self, line: int = -1, column: int = -1) -> None:
        super().__init__(line, column)

    def can_be_true_default(self) -> bool:
        return False

    def __hash__(self) -> int:
        return hash(NoneType)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, NoneType)

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_none_type(self)



class ObjectType(Type):
    __slots__ = ("type", "_hash")

    def __init__(
        self,
        typ: refpy.nodes.TypeInfo,
        line: int = -1,
        column: int = -1,
    ) -> None:
        super().__init__(line, column)
        self.type = typ
        
        self._hash = -1


    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_instance(self)

    def __hash__(self) -> int:
        if self._hash == -1:
            self._hash = hash((self.type))
        return self._hash

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ObjectType):
            return NotImplemented
        return self.type == other.type

class FunctionStub(Type):

    __slots__ = (
        "arg_types",  
        "arg_kinds",  
        "arg_names",  
        "min_args",  
        "ret_type",  
        "name",  
        "definition",  
        "ref_arg_types",
        "ref_ret_type"
    )

    def __init__(
        self,
        arg_types: Sequence[Expression|None],
        arg_kinds: list[ArgKind],
        arg_names: Sequence[str | None],
        ret_type: Expression|None,
        name: str | None = None,
        definition: SymbolNode | None = None,
        line: int = -1,
        column: int = -1,
        ref_arg_types = None,
        ref_ret_type = None
    ) -> None:
        super().__init__(line, column)
        assert len(arg_types) == len(arg_kinds) == len(arg_names)
        self.arg_types = list(arg_types)
        self.arg_kinds = arg_kinds
        self.arg_names = list(arg_names)
        self.min_args = arg_kinds.count(ARG_POS)
        self.ret_type = ret_type
        assert not name or "<bound method" not in name
        self.name = name
        self.definition = definition
        self.ref_arg_types = ref_arg_types
        self.ref_ret_type = ref_ret_type

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_callable_stub(self)

    def get_name(self) -> str | None:
        return self.name
    
    def __hash__(self) -> int:
        return hash((self.ret_type,self.name, tuple(self.arg_types),  tuple(self.arg_names), tuple(self.arg_kinds)))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FunctionType):
            return (
                self.ret_type == other.ret_type
                and self.arg_types == other.arg_types
                and self.arg_names == other.arg_names
                and self.arg_kinds == other.arg_kinds
                and self.name == other.name
            )
        else:
            return NotImplemented
class FunctionType(Type):
    

    __slots__ = (
        "arg_types",  
        "arg_kinds",  
        "arg_names",  
        "min_args",  
        "ret_type",  
        "name",  
        "definition",  
        "ref_arg_types",
        "ref_ret_type"
    )

    def __init__(
        self,
        arg_types: Sequence[Type],
        arg_kinds: list[ArgKind],
        arg_names: Sequence[str | None],
        ret_type: Type,
        name: str | None = None,
        definition: SymbolNode | None = None,
        line: int = -1,
        column: int = -1,
        ref_arg_types = None,
        ref_ret_type = None
    ) -> None:
        super().__init__(line, column)
        assert len(arg_types) == len(arg_kinds) == len(arg_names)
        self.arg_types = list(arg_types)
        self.arg_kinds = arg_kinds
        self.arg_names = list(arg_names)
        self.min_args = arg_kinds.count(ARG_POS)
        self.ret_type = ret_type
        assert not name or "<bound method" not in name
        self.name = name
        self.definition = definition
        self.ref_arg_types = ref_arg_types
        self.ref_ret_type = ref_ret_type

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_callable_type(self)

    def get_name(self) -> str | None:
        return self.name
    
    def __hash__(self) -> int:
        return hash((self.ret_type,self.name, tuple(self.arg_types),  tuple(self.arg_names), tuple(self.arg_kinds)))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, FunctionType):
            return (
                self.ret_type == other.ret_type
                and self.arg_types == other.arg_types
                and self.arg_names == other.arg_names
                and self.arg_kinds == other.arg_kinds
                and self.name == other.name
            )
        else:
            return NotImplemented

class TupleType(Type):
    

    __slots__ = ("items", "partial_fallback")

    items: list[Type]

    def __init__(
        self,
        items: list[Type],
        line: int = -1,
        column: int = -1,
    ) -> None:
        super().__init__(line, column)
        self.items = items

    def length(self) -> int:
        return len(self.items)

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_tuple_type(self)

    def __hash__(self) -> int:
        return hash((tuple(self.items)))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, TupleType):
            return NotImplemented
        return self.items == other.items


class UnionType(Type):
    
    __slots__ = ("items")

    def __init__(
        self,
        items: Sequence[Type],
        line: int = -1,
        column: int = -1,
    ) -> None:
        super().__init__(line, column)
        self.items = items
    def __hash__(self) -> int:
        return hash(frozenset(self.items))

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnionType):
            return NotImplemented
        return frozenset(self.items) == frozenset(other.items)

    def length(self) -> int:
        return len(self.items)

    def accept(self, visitor: TypeVisitor[T]) -> T:
        return visitor.visit_union_type(self)

class TypeVisitor(Generic[T]):
    @abstractmethod
    def visit_any(self, t: AnyType) -> T:
        pass
    @abstractmethod
    def visit_none_type(self, t: NoneType) -> T:
        pass
    @abstractmethod
    def visit_instance(self, t: ObjectType) -> T:
        pass
    @abstractmethod
    def visit_callable_stub(self, t: FunctionStub) -> T:
        pass
    @abstractmethod
    def visit_callable_type(self, t: FunctionType) -> T:
        pass
    @abstractmethod
    def visit_tuple_type(self, t: TupleType) -> T:
        pass
    @abstractmethod
    def visit_union_type(self, t: UnionType) -> T:
        pass
class TypeStrVisitor(TypeVisitor[str]):
    

    def __init__(self, options: Options) -> None:
        self.any_as_dots = False
        self.options = options

    def visit_any(self, t: AnyType) -> str:
        return "Any"

    def visit_none_type(self, t: NoneType) -> str:
        return "None"


    def visit_instance(self, t: ObjectType) -> str:
        s = t.type.fullname or t.type.name or "<???>"
        return s
    def visit_callable_stub(self, t: FunctionStub) -> str:
        return "a callable stub"
    def visit_callable_type(self, t: FunctionType) -> str:

        num_skip = 0

        s = ""
        bare_asterisk = False
        for i in range(len(t.arg_types) - num_skip):
            if s != "":
                s += ", "
            if t.arg_kinds[i].is_named() and not bare_asterisk:
                s += "*, "
                bare_asterisk = True
            if t.arg_kinds[i] == ARG_STAR:
                s += "*"
            if t.arg_kinds[i] == ARG_STAR2:
                s += "**"
            name = t.arg_names[i]
            if name:
                s += name + ": "
            type_str = t.arg_types[i].accept(self)
            s += type_str
            if t.arg_kinds[i].is_optional():
                s += " ="

        s = f"({s})"

        s += f" -> {t.ret_type.accept(self)}"


        return f"def {s}"

    def visit_tuple_type(self, t: TupleType) -> str:
        s = self.list_str(t.items)
        return f"{'tuple'}[{s}]"

    def visit_union_type(self, t: UnionType) -> str:
        s = self.list_str(t.items)
        return f"Union[{s}]"
    def list_str(self, a: Iterable[Type]) -> str:
        
        res = []
        for t in a:
            res.append(t.accept(self))
        return ", ".join(res)


