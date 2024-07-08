

from __future__ import annotations

import os
from abc import abstractmethod
from collections import defaultdict
from enum import Enum, unique
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Union,
    cast,
)
from typing_extensions import Final, TypeAlias as _TypeAlias, TypeGuard


from refpy.options import Options
from refpy.visitor import ExpressionVisitor, NodeVisitor, StatementVisitor


class Context:
    __slots__ = ("line", "column", "end_line", "end_column")

    def __init__(self, line: int = -1, column: int = -1) -> None:
        self.line = line
        self.column = column
        self.end_line: int | None = None
        self.end_column: int | None = None

    def set_line(
        self,
        target: Context | int,
        column: int | None = None,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        
        if isinstance(target, int):
            self.line = target
        else:
            self.line = target.line
            self.column = target.column
            self.end_line = target.end_line
            self.end_column = target.end_column

        if column is not None:
            self.column = column

        if end_line is not None:
            self.end_line = end_line

        if end_column is not None:
            self.end_column = end_column


T = TypeVar("T")




class Node(Context):
    

    __slots__ = ()

    def __str__(self) -> str:
        return "Bare Node"

    def accept(self, visitor: NodeVisitor[T], *args) -> T:
        raise RuntimeError("Not implemented")
class Statement(Node):
    

    __slots__ = ()

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        raise RuntimeError("Not implemented")

class Expression(Node):

    __slots__ = ()

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        raise RuntimeError("Not implemented")

Lvalue: _TypeAlias = Expression

class SymbolNode(Node):
    
    __slots__ = ()

    @property
    @abstractmethod
    def name(self) -> str:
        pass

    
    @property
    @abstractmethod
    def fullname(self) -> str:
        pass

class RefpyFile(SymbolNode):
    

    __slots__ = (
        "_fullname",
        "path",
        "defs",
        "names",
        "imports",
        "ignored_lines",
        "is_stub",
    )

    __match_args__ = ("name", "path", "defs")

    
    _fullname: str
    
    path: str
    
    defs: list[Statement]
    
    names: SymbolTable
    imports: list[ImportBase]
    ignored_lines: dict[int, list[str]]
    is_stub: bool

    def __init__(
        self,
        defs: list[Statement],
        imports: list[ImportBase],
        ignored_lines: dict[int, list[str]] | None = None,
    ) -> None:
        super().__init__()
        self.defs = defs
        self.line = 1  
        self.column = 0  
        self.imports = imports
        if ignored_lines:
            self.ignored_lines = ignored_lines
        else:
            self.ignored_lines = {}

        self.path = ""
        self.is_stub = False

    @property
    def name(self) -> str:
        return "" if not self._fullname else self._fullname.split(".")[-1]

    @property
    def fullname(self) -> str:
        return self._fullname

    def accept(self, visitor: NodeVisitor[T], *args) -> T:
        return visitor.visit_refpy_file(self)

    def is_package_init_file(self) -> bool:
        return len(self.path) != 0 and os.path.basename(self.path).startswith("__init__.")

class ImportBase(Statement):
    

    __slots__ = ()

    def __init__(self) -> None:
        super().__init__()


class Import(ImportBase):
    

    __slots__ = ("ids",)

    __match_args__ = ("ids",)

    ids: list[tuple[str, str | None]]  

    def __init__(self, ids: list[tuple[str, str | None]]) -> None:
        super().__init__()
        self.ids = ids

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_import(self, *args)


class ImportFrom(ImportBase):
    

    __slots__ = ("id", "names", "relative")

    __match_args__ = ("id", "names", "relative")

    id: str
    relative: int
    names: list[tuple[str, str | None]]  

    def __init__(self, id: str, relative: int, names: list[tuple[str, str | None]]) -> None:
        super().__init__()
        self.id = id
        self.names = names
        self.relative = relative

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_import_from(self, *args)


class ImportAll(ImportBase):
    

    __slots__ = ("id", "relative")

    __match_args__ = ("id", "relative")

    id: str
    relative: int

    def __init__(self, id: str, relative: int) -> None:
        super().__init__()
        self.id = id
        self.relative = relative

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_import_all(self, *args)





class Argument(Node):
    

    __slots__ = ("variable", "type_annotation", "initializer", "kind", "pos_only", "ref_type")

    __match_args__ = ("variable", "type_annotation", "initializer", "kind", "pos_only", "ref_type")

    def __init__(
        self,
        variable: Var,
        type_annotation: Expression | None,
        initializer: Expression | None,
        kind: ArgKind,
        pos_only: bool = False,
        ref_type = None,
    ) -> None:
        super().__init__()
        self.variable = variable
        self.type_annotation = type_annotation
        self.initializer = initializer
        self.kind = kind  
        self.pos_only = pos_only
        self.ref_type = ref_type
    def set_line(
        self,
        target: Context | int,
        column: int | None = None,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
        super().set_line(target, column, end_line, end_column)

        if self.initializer and self.initializer.line < 0:
            self.initializer.set_line(self.line, self.column, self.end_line, self.end_column)

        self.variable.set_line(self.line, self.column, self.end_line, self.end_column)

class FuncDef(SymbolNode, Statement):

    __slots__ = (
        "type",
        "info",
        "_fullname",
        "arguments",
        "arg_names",
        "arg_kinds",
        "min_args",
        "max_pos",
        "body",
        "ref_type",
        "_name"
    )

    __deletable__ = ("arguments", "max_pos", "min_args")

    def __init__(
        self,
        name: str = "",
        arguments: Optional[list[Argument]] = None,
        body: Optional[Block] = None,
        typ: Any = None,
        ref_type: Any = None
    ) -> None:
        super().__init__()
        
        self.type: Any = typ
        self.info: TypeInfo|None = None
        self._fullname = ""

        self.arguments = arguments or []
        self.arg_names = [None if arg.pos_only else arg.variable.name for arg in self.arguments]
        self.arg_kinds = [arg.kind for arg in self.arguments]
        self.max_pos = self.arg_kinds.count(ARG_POS) + self.arg_kinds.count(ARG_OPT)
        self.body = body or Block([])
        self.ref_type = ref_type

        self.min_args = 0
        for i in range(len(self.arguments)):
            if self.arguments[i] is None and i < self.max_fixed_argc():
                self.min_args = i + 1

        self._name = name

    def max_fixed_argc(self) -> int:
        return self.max_pos

    def is_dynamic(self) -> bool:
        return self.type is None

    @property
    def name(self) -> str:
        return self._name

    @property
    def fullname(self) -> str:
        return self._fullname

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_func_def(self, *args)
    
class Var(SymbolNode):
    

    __slots__ = (
        "_name",
        "_fullname",
        "info",
        "type",
        "ref_type",
    )

    __match_args__ = ("name", "type")

    def __init__(self, name: str, type: Any | None = None) -> None:
        super().__init__()
        self._name = name  
        
        self._fullname = ""  
        
        self.info:TypeInfo|None = None
        self.type: Any | None = type  
        self.ref_type: Any = None
    @property
    def name(self) -> str:
        return self._name

    @property
    def fullname(self) -> str:
        return self._fullname

    def accept(self, visitor: NodeVisitor[T], *args) -> T:
        return visitor.visit_var(self, *args)


class ClassDef(Statement):
    

    __slots__ = (
        "name",
        "_fullname",
        "defs",
        "base_type_exprs",
        "info",
        "decorators",
    )

    __match_args__ = ("name", "defs")

    name: str  
    _fullname: str  
    defs: Block
    base_type_exprs: list[Expression]
    info: Optional[TypeInfo]  
    decorators: list[Expression]

    def __init__(
        self,
        name: str,
        defs: Block,
        base_type_exprs: list[Expression] | None = None,
    ) -> None:
        super().__init__()
        self.name = name
        self._fullname = ""
        self.defs = defs
        self.base_type_exprs = base_type_exprs or []
        self.info = None
        self.decorators = []

    @property
    def fullname(self) -> str:
        return self._fullname

    @fullname.setter
    def fullname(self, v: str) -> None:
        self._fullname = v

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_class_def(self, *args)



class Block(Statement):
    __slots__ = ("body")

    __match_args__ = ("body")

    def __init__(self, body: list[Statement]) -> None:
        super().__init__()
        self.body = body

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_block(self, *args)





class ExpressionStmt(Statement):
    

    __slots__ = ("expr",)

    __match_args__ = ("expr",)

    expr: Expression

    def __init__(self, expr: Expression) -> None:
        super().__init__()
        self.expr = expr

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_expression_stmt(self, *args)


class AssignmentStmt(Statement):
    __slots__ = (
        "lvalues",
        "rvalue",
        "type_ann",
        "ref_type", 
        "type"
    )

    __match_args__ = ("lvalues", "rvalues", "type", "ref_type")

    lvalues: list[Lvalue]
    
    rvalue: Expression
    
    type_ann: Expression | None
    type: Any
    
    def __init__(
        self,
        lvalues: list[Lvalue],
        rvalue: Expression,
        type_ann: Expression | None = None,
        ref_type = None
    ) -> None:
        super().__init__()
        self.lvalues = lvalues
        self.rvalue = rvalue
        self.type_ann = type_ann
        self.ref_type = ref_type

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_assignment_stmt(self, *args)


class WhileStmt(Statement):
    __slots__ = ("expr", "body", "else_body")

    __match_args__ = ("expr", "body", "else_body")

    expr: Expression
    body: Block
    else_body: Block | None

    def __init__(self, expr: Expression, body: Block, else_body: Block | None) -> None:
        super().__init__()
        self.expr = expr
        self.body = body
        self.else_body = else_body

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_while_stmt(self, *args)


class ReturnStmt(Statement):
    __slots__ = ("expr",)

    __match_args__ = ("expr",)

    expr: Expression | None

    def __init__(self, expr: Expression | None) -> None:
        super().__init__()
        self.expr = expr

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_return_stmt(self, *args)


class AssertStmt(Statement):
    __slots__ = ("expr", "msg")

    __match_args__ = ("expr", "msg")

    expr: Expression
    msg: Expression | None

    def __init__(self, expr: Expression, msg: Expression | None = None) -> None:
        super().__init__()
        self.expr = expr
        self.msg = msg

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_assert_stmt(self, *args)


class BreakStmt(Statement):
    __slots__ = ()

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_break_stmt(self, *args)


class ContinueStmt(Statement):
    __slots__ = ()

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_continue_stmt(self, *args)


class PassStmt(Statement):
    __slots__ = ()

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_pass_stmt(self, *args)

SymbolTable = Dict[str, SymbolNode]
class IfStmt(Statement):
    __slots__ = ("expr", "body", "else_body")

    __match_args__ = ("expr", "body", "else_body")

    expr: list[Expression]
    body: list[Block]
    else_body: Block | None

    def __init__(self, expr: list[Expression], body: list[Block], else_body: Block | None) -> None:
        super().__init__()
        self.expr = expr
        self.body = body
        self.else_body = else_body

    def accept(self, visitor: StatementVisitor[T], *args) -> T:
        return visitor.visit_if_stmt(self, *args)





class IntExpr(Expression):
    

    __slots__ = ("value",)

    __match_args__ = ("value",)

    value: int  

    def __init__(self, value: int) -> None:
        super().__init__()
        self.value = value

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_int_expr(self, *args)




class StrExpr(Expression):
    

    __slots__ = ("value",)

    __match_args__ = ("value",)

    value: str  

    def __init__(self, value: str) -> None:
        super().__init__()
        self.value = value

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_str_expr(self, *args)


class FloatExpr(Expression):
    

    __slots__ = ("value",)

    __match_args__ = ("value",)

    value: float  

    def __init__(self, value: float) -> None:
        super().__init__()
        self.value = value

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_float_expr(self, *args)

class EllipsisExpr(Expression):
    

    __slots__ = ()

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_ellipsis(self, *args)

class RefExpr(Expression):
    

    __slots__ = (
        "node",
        "_fullname",
    )

    def __init__(self) -> None:
        super().__init__()
        
        self.node: SymbolNode | None = None
        
        self._fullname = ""


    @property
    def fullname(self) -> str:
        return self._fullname

    @fullname.setter
    def fullname(self, v: str) -> None:
        self._fullname = v


class NameExpr(RefExpr):
    

    __slots__ = ("name")

    __match_args__ = ("name", "node")

    def __init__(self, name: str) -> None:
        super().__init__()
        self.name = name  

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_name_expr(self, *args)


class MemberExpr(RefExpr):
    

    __slots__ = ("expr", "name", "def_var")

    __match_args__ = ("expr", "name", "node")

    def __init__(self, expr: Expression, name: str) -> None:
        super().__init__()
        self.expr = expr
        self.name = name
        self.def_var: Var | None = None

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_member_expr(self, *args)



@unique
class ArgKind(Enum):
    
    ARG_POS = 0
    
    ARG_OPT = 1
    
    ARG_STAR = 2
    
    ARG_NAMED = 3
    
    ARG_STAR2 = 4
    
    ARG_NAMED_OPT = 5

    def is_positional(self, star: bool = False) -> bool:
        return self == ARG_POS or self == ARG_OPT or (star and self == ARG_STAR)

    def is_named(self, star: bool = False) -> bool:
        return self == ARG_NAMED or self == ARG_NAMED_OPT or (star and self == ARG_STAR2)

    def is_required(self) -> bool:
        return self == ARG_POS or self == ARG_NAMED

    def is_optional(self) -> bool:
        return self == ARG_OPT or self == ARG_NAMED_OPT

    def is_star(self) -> bool:
        return self == ARG_STAR or self == ARG_STAR2


ARG_POS: Final = ArgKind.ARG_POS
ARG_OPT: Final = ArgKind.ARG_OPT
ARG_STAR: Final = ArgKind.ARG_STAR
ARG_NAMED: Final = ArgKind.ARG_NAMED
ARG_STAR2: Final = ArgKind.ARG_STAR2
ARG_NAMED_OPT: Final = ArgKind.ARG_NAMED_OPT


class CallExpr(Expression):
    

    __slots__ = ("callee", "args", "arg_kinds", "arg_names", "annotation")

    __match_args__ = ("callee", "args", "arg_kinds", "arg_names")

    def __init__(
        self,
        callee: Expression,
        args: list[Expression],
        arg_kinds: list[ArgKind],
        arg_names: list[str | None],
    ) -> None:
        super().__init__()
        if not arg_names:
            arg_names = [None] * len(args)

        self.callee = callee
        self.args = args
        self.arg_kinds = arg_kinds  
        
        self.arg_names: list[str | None] = arg_names
        self.annotation = None

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_call_expr(self, *args)

class IndexExpr(Expression):
    

    __slots__ = ("base", "index")

    __match_args__ = ("base", "index")

    base: Expression
    index: Expression

    def __init__(self, base: Expression, index: Expression) -> None:
        super().__init__()
        self.base = base
        self.index = index

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_index_expr(self, *args)


class UnaryExpr(Expression):
    

    __slots__ = ("op", "expr")

    __match_args__ = ("op", "expr")

    op: str 
    expr: Expression

    def __init__(self, op: str, expr: Expression) -> None:
        super().__init__()
        self.op = op
        self.expr = expr

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_unary_expr(self, *args)

class OpExpr(Expression):
    

    __slots__ = ("op", "left", "right")

    __match_args__ = ("left", "op", "right")

    op: str  
    left: Expression
    right: Expression

    def __init__( self, op: str, left: Expression, right: Expression ) -> None:
        super().__init__()
        self.op = op
        self.left = left
        self.right = right

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_op_expr(self, *args)


class ComparisonExpr(Expression):
    

    __slots__ = ("operators", "operands")

    __match_args__ = ("operands", "operators")

    operators: list[str]
    operands: list[Expression]

    def __init__(self, operators: list[str], operands: list[Expression]) -> None:
        super().__init__()
        self.operators = operators
        self.operands = operands

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_comparison_expr(self, *args)



class SuperExpr(Expression):
    

    __slots__ = ("name", "info", "call")

    __match_args__ = ("name", "call", "info")

    name: str
    info: TypeInfo | None  
    call: CallExpr  

    def __init__(self, name: str, call: CallExpr) -> None:
        super().__init__()
        self.name = name
        self.call = call
        self.info = None

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_super_expr(self, *args)



class ListExpr(Expression):
    

    __slots__ = ("items",)

    __match_args__ = ("items",)

    items: list[Expression]

    def __init__(self, items: list[Expression]) -> None:
        super().__init__()
        self.items = items

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_list_expr(self, *args)


class DictExpr(Expression):
    

    __slots__ = ("items",)

    __match_args__ = ("items",)

    items: list[tuple[Expression | None, Expression]]

    def __init__(self, items: list[tuple[Expression | None, Expression]]) -> None:
        super().__init__()
        self.items = items

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_dict_expr(self, *args)


class TupleExpr(Expression):
    

    __slots__ = ("items",)

    __match_args__ = ("items",)

    items: list[Expression]

    def __init__(self, items: list[Expression]) -> None:
        super().__init__()
        self.items = items

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_tuple_expr(self, *args)


class SetExpr(Expression):
    

    __slots__ = ("items",)

    __match_args__ = ("items",)

    items: list[Expression]

    def __init__(self, items: list[Expression]) -> None:
        super().__init__()
        self.items = items

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_set_expr(self, *args)

class ConditionalExpr(Expression):
    

    __slots__ = ("cond", "if_expr", "else_expr")

    __match_args__ = ("if_expr", "cond", "else_expr")

    cond: Expression
    if_expr: Expression
    else_expr: Expression

    def __init__(self, cond: Expression, if_expr: Expression, else_expr: Expression) -> None:
        super().__init__()
        self.cond = cond
        self.if_expr = if_expr
        self.else_expr = else_expr

    def accept(self, visitor: ExpressionVisitor[T], *args) -> T:
        return visitor.visit_conditional_expr(self, *args)
    
class TypeInfo(SymbolNode):

    __slots__ = (
        "_fullname",
        "module_name",
        "defn",
        "names",
        "base",
        "bases",
        "typeddict_type",
    )

    _fullname: str  
    
    module_name: str
    defn: ClassDef 
    names: SymbolTable
    base: TypeInfo
    bases: list[TypeInfo]

    def __init__(self, names: SymbolTable, defn: ClassDef, module_name: str) -> None:
        
        super().__init__()
        self._fullname = defn.fullname
        self.names = names
        self.defn = defn
        self.module_name = module_name
        self.bases = []
        self.typeddict_type = None


    @property
    def name(self) -> str:
        
        return self.defn.name

    @property
    def fullname(self) -> str:
        return self._fullname

    def get(self, name: str) -> SymbolNode | None:
        for cls in self.bases:
            n = cls.names.get(name)
            if n:
                return n
        return None

    def get_containing_type_info(self, name: str) -> TypeInfo | None:
        for cls in self.bases:
            if name in cls.names:
                return cls
        return None


    def __getitem__(self, name: str) -> SymbolNode:
        n = self.get(name)
        if n:
            return n
        else:
            raise KeyError(name)

    def __repr__(self) -> str:
        return f"<TypeInfo {self.fullname}>"

    def __str__(self) -> str:
        
        return self.fullname
