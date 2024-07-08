from __future__ import annotations

import copy
import re
import sys
import warnings
from typing import Any, Callable, List, Optional, Sequence, TypeVar, Union, cast
from typing_extensions import Final, Literal, overload

from refpy.refinements import transform_refinement, RefType, Refinement, mkTrue, vv
from refpy.errors import ErrorCollectors
from refpy.nodes import (
    ARG_NAMED,
    ARG_NAMED_OPT,
    ARG_OPT,
    ARG_POS,
    ARG_STAR,
    ARG_STAR2,
    ArgKind,
    Argument,
    AssertStmt,
    AssignmentStmt,
    Block,
    BreakStmt,
    CallExpr,
    ClassDef,
    ComparisonExpr,
    ConditionalExpr,
    ContinueStmt,
    DictExpr,
    EllipsisExpr,
    Expression,
    ExpressionStmt,
    FloatExpr,
    FuncDef,
    IfStmt,
    Import,
    ImportAll,
    ImportBase,
    ImportFrom,
    IndexExpr,
    IntExpr,
    ListExpr,
    MemberExpr,
    RefpyFile,
    NameExpr,
    Node,
    OpExpr,
    PassStmt,
    RefExpr,
    ReturnStmt,
    SetExpr,
    Statement,
    StrExpr,
    SuperExpr,
    TupleExpr,
    UnaryExpr,
    Var,
    WhileStmt,
)
from refpy.options import Options
from refpy.types import (
    FunctionStub,
    Type,
    Type,
)
import ast


PY_MINOR_VERSION: Final = sys.version_info[1]

import ast as ast3
from ast import (
    AST,
    Attribute,
    Call,
    Ellipsis as ast3_Ellipsis,
    Expression as ast3_Expression,
    FunctionType,
    Index,
    Name,
    Starred,
    Str,
)

def ast3_parse(
    source: str | bytes, filename: str, mode: str, feature_version: int = PY_MINOR_VERSION
) -> AST:
    return ast3.parse( source,  filename,   mode, type_comments=True,   feature_version=feature_version, )

Constant = ast3.Constant


N = TypeVar("N", bound=Node)


TYPE_IGNORE_PATTERN: Final = re.compile(r"[^#]*#\s*type:\s*ignore\s*(.*)")


def source_to_tree(
    source: str | bytes,
    fnam: str,
    module: str | None,
    errors: ErrorCollectors | None = None,
    options: Options | None = None,
) -> RefpyFile:
    if options is None:
        options = Options()
    if errors is None:
        errors = ErrorCollectors(options)
        raise_on_error = True
    errors.set_file(fnam, module, options=options)
    is_stub_file = fnam.endswith(".pyi")
    with warnings.catch_warnings():
        warnings.filterwarnings("ignore", category=DeprecationWarning)
        ast = ast3_parse(source, fnam, "exec")

    tree = ASTConverter(options=options,  is_stub=is_stub_file, errors=errors).visit(ast)
    tree.path = fnam
    tree.is_stub = is_stub_file

    assert isinstance(tree, RefpyFile)
    return tree


def parse_type_ignore_tag(tag: str | None) -> list[str] | None:
    if not tag or tag.strip() == "" or tag.strip().startswith("#"):
        
        return []
    m = re.match(r"\s*\[([^]#]*)\]\s*(#.*)?$", tag)
    if m is None:
        
        return None
    return [code.strip() for code in m.group(1).split(",")]


def parse_type_comment_expr(
    type_comment: str, line: int, column: int, errors: ErrorCollectors | None
) -> ast3_Expression:
    
    typ = ast3_parse(type_comment, "<type_comment>", "eval")
    assert isinstance(typ, ast3_Expression)
    return typ



class ASTConverter:
    def __init__(
        self,
        options: Options,
        is_stub: bool,
        errors: ErrorCollectors,
    ) -> None:
        
        self.class_and_function_stack: list[Literal["C", "D", "F", "L"]] = []
        self.imports: list[ImportBase] = []
        self.options = options
        self.is_stub = is_stub
        self.errors = errors
        self.type_ignores: dict[int, list[str]] = {}


    def visit(self, node: AST | None) -> Any:
        if node is None:
            return None
        typeobj = type(node)
        method = "visit_" + node.__class__.__name__
        visitor = getattr(self, method)
        return visitor(node)

    def set_line(self, node: N, n) -> N:
        node.line = n.lineno
        node.column = n.col_offset
        node.end_line = getattr(n, "end_lineno", None)
        node.end_column = getattr(n, "end_col_offset", None)

        return node

    def translate_opt_expr_list(self, l: Sequence[AST | None]) -> list[Expression | None]:
        res: list[Expression | None] = []
        for e in l:
            exp = self.visit(e)
            res.append(exp)
        return res

    def translate_expr_list(self, l: Sequence[AST]) -> list[Expression]:
        return cast(List[Expression], self.translate_opt_expr_list(l))

    def get_lineno(self, node: ast3.expr | ast3.stmt) -> int:
        if (
            isinstance(node, (ast3.ClassDef, ast3.FunctionDef))
            and node.decorator_list
        ):
            return node.decorator_list[0].lineno
        return node.lineno

    def translate_stmt_list(self,stmts: Sequence[ast3.stmt]) -> list[Statement]:
        res: list[Statement] = []
        for stmt in stmts:
            node = self.visit(stmt)
            res.append(node)

        return res


    op_map: Final[dict[type[AST], str]] = {
        ast3.Add: "+",
        ast3.Sub: "-",
        ast3.Mult: "*",
        ast3.MatMult: "@",
        ast3.Div: "/",
        ast3.Mod: "%",
        ast3.Pow: "**",
        ast3.LShift: "<<",
        ast3.RShift: ">>",
        ast3.BitOr: "|",
        ast3.BitXor: "^",
        ast3.BitAnd: "&",
        ast3.FloorDiv: "//",
    }

    def from_operator(self, op: ast3.operator) -> str:
        op_name = ASTConverter.op_map.get(type(op))
        if op_name is None:
            raise RuntimeError("Unknown operator " + str(type(op)))
        else:
            return op_name

    comp_op_map: Final[dict[type[AST], str]] = {
        ast3.Gt: ">",
        ast3.Lt: "<",
        ast3.Eq: "==",
        ast3.GtE: ">=",
        ast3.LtE: "<=",
        ast3.NotEq: "!=",
        ast3.Is: "is",
        ast3.IsNot: "is not",
        ast3.In: "in",
        ast3.NotIn: "not in",
    }

    def from_comp_operator(self, op: ast3.cmpop) -> str:
        op_name = ASTConverter.comp_op_map.get(type(op))
        if op_name is None:
            raise RuntimeError("Unknown comparison operator " + str(type(op)))
        else:
            return op_name

    def set_block_lines(self, b: Block, stmts: Sequence[ast3.stmt]) -> None:
        first, last = stmts[0], stmts[-1]
        b.line = first.lineno
        b.column = first.col_offset
        b.end_line = getattr(last, "end_lineno", None)
        b.end_column = getattr(last, "end_col_offset", None)
        if not b.body:
            return

    def as_block(self, stmts: list[ast3.stmt]) -> Block | None:
        b = None
        if stmts:
            b = Block(self.translate_stmt_list(stmts))
            self.set_block_lines(b, stmts)
        return b

    def as_required_block(
        self, stmts: list[ast3.stmt] ) -> Block:
        assert stmts  
        b = Block(self.translate_stmt_list(stmts))
        self.set_block_lines(b, stmts)
        return b
    
    def visit_Module(self, mod: ast3.Module) -> RefpyFile:
        self.type_ignores = {}
        for ti in mod.type_ignores:
            parsed = parse_type_ignore_tag(ti.tag)
            if parsed is not None:
                self.type_ignores[ti.lineno] = parsed
            else:
                self.errors.report(ti.lineno, None, "type ignore tag syntax error")
        body = self.translate_stmt_list(mod.body)
        return RefpyFile(body, self.imports, self.type_ignores)

    def visit_FunctionDef(self, n: ast3.FunctionDef) -> FuncDef:
        self.class_and_function_stack.append("D")

        lineno = n.lineno
        args = self.transform_args(n.args, lineno,)

        arg_kinds = [arg.kind for arg in args]
        arg_names = [None if arg.pos_only else arg.variable.name for arg in args]

        arg_types: list[Expression | None] = []
        
        arg_types = [a.type_annotation for a in args]
        return_type = self.visit(n.returns)
        if n.type_comment is not None and 'Ref[' in n.type_comment:
            func_type_ast = ast3_parse(n.type_comment, "<func_type>", "func_type")
            assert isinstance(func_type_ast, FunctionType)
            ret_ref = transform_refinement(func_type_ast.returns)
        else:
            ret_ref = [mkTrue()]

        func_type = None
        if any(arg_types) or return_type:
            if len(arg_types) > len(arg_kinds):
                self.errors.report(n.lineno, None, "too many args")
            elif len(arg_types) < len(arg_kinds):
                self.errors.report(n.lineno, None, "too few args")
            else:
                func_type = FunctionStub(
                    arg_types,
                    arg_kinds,
                    arg_names,
                    return_type,
                )

        
        end_line = getattr(n, "end_lineno", None)
        end_column = getattr(n, "end_col_offset", None)

        self.class_and_function_stack.pop()
        self.class_and_function_stack.append("F")
        body = self.as_required_block(n.body)
        if func_type:
            ref_arg_types = []
            normal_arg_types = func_type.arg_types
            for arg, argNT in zip(args, normal_arg_types):
                if arg.ref_type:
                    ref = arg.ref_type
                else:
                    ref = [mkTrue()]
                ref_arg_types.append(ref)
            func_type = FunctionStub(normal_arg_types, arg_kinds, arg_names, return_type, ref_arg_types=ref_arg_types, ref_ret_type=ret_ref)
        func_def = FuncDef(n.name, args, body, func_type, None)
        if func_type is not None:
            func_type.definition = func_def
            func_type.line = lineno


        func_def.set_line(lineno, n.col_offset, end_line, end_column)
        retval = func_def
        self.class_and_function_stack.pop()
        return retval


    def transform_args(
        self, args: ast3.arguments, line: int
    ) -> list[Argument]:
        new_args = []
        names: list[ast3.arg] = []
        posonlyargs = getattr(args, "posonlyargs", cast(List[ast3.arg], []))
        args_args = posonlyargs + args.args
        args_defaults = args.defaults
        num_no_defaults = len(args_args) - len(args_defaults)
        
        for i, a in enumerate(args_args[:num_no_defaults]):
            pos_only = i < len(posonlyargs)
            new_args.append(self.make_argument(a, None, ARG_POS, pos_only))
            names.append(a)

        
        for i, (a, d) in enumerate(zip(args_args[num_no_defaults:], args_defaults)):
            pos_only = num_no_defaults + i < len(posonlyargs)
            new_args.append(self.make_argument(a, d, ARG_OPT, pos_only))
            names.append(a)

        
        if args.vararg is not None:
            new_args.append(self.make_argument(args.vararg, None, ARG_STAR))
            names.append(args.vararg)

        
        for a, kd in zip(args.kwonlyargs, args.kw_defaults):
            new_args.append(
                self.make_argument(
                    a, kd, ARG_NAMED if kd is None else ARG_NAMED_OPT
                )
            )
            names.append(a)

        
        if args.kwarg is not None:
            new_args.append(self.make_argument(args.kwarg, None, ARG_STAR2))
            names.append(args.kwarg)

        return new_args

    def make_argument(
        self,
        arg: ast3.arg,
        default: ast3.expr | None,
        kind: ArgKind,
        pos_only: bool = False,
    ) -> Argument:
        annotation = arg.annotation
        type_comment = arg.type_comment
        arg_type = None
        if annotation is not None:
            arg_type = self.visit(annotation)
        else:
            assert False

        if type_comment is not None and 'Ref[' in type_comment:
            expr = ast3_parse(type_comment, "<type_comment>", "eval")
            assert isinstance(expr, ast.Expression)
            ref_type = transform_refinement(expr.body)
        else:
            ref_type = [mkTrue()]

        argument = Argument(Var(arg.arg), arg_type, self.visit(default), kind, pos_only, ref_type)
        argument.set_line(
            arg.lineno,
            arg.col_offset,
            getattr(arg, "end_lineno", None),
            getattr(arg, "end_col_offset", None),
        )
        return argument

    def visit_ClassDef(self, n: ast3.ClassDef) -> ClassDef:
        self.class_and_function_stack.append("C")

        cdef = ClassDef(
            n.name,
            self.as_required_block(n.body),
            self.translate_expr_list(n.bases),
        )
        cdef.decorators = self.translate_expr_list(n.decorator_list)
        cdef.line = n.lineno
        cdef.column = n.col_offset
        cdef.end_line = getattr(n, "end_lineno", None)
        cdef.end_column = getattr(n, "end_col_offset", None)
        self.class_and_function_stack.pop()
        return cdef

    
    def visit_Return(self, n: ast3.Return) -> ReturnStmt:
        node = ReturnStmt(self.visit(n.value))
        return self.set_line(node, n)


    
    def visit_Assign(self, n: ast3.Assign) -> AssignmentStmt:
        lvalues = self.translate_expr_list(n.targets)
        rvalue = self.visit(n.value)

        if n.type_comment is not None and 'Ref[' in n.type_comment:
            typ = self.visit(parse_type_comment_expr(n.type_comment.split('[')[1], n.lineno, n.col_offset, None).body)
            expr = ast3_parse(n.type_comment, "<type_comment>", "eval")
            assert isinstance(expr, ast.Expression)
            ref_type = transform_refinement(expr.body)
        else:
            typ = None
            ref_type = None
        s = AssignmentStmt(lvalues, rvalue, type_ann=typ, ref_type=ref_type)
        return self.set_line(s, n)

    
    def visit_AnnAssign(self, n: ast3.AnnAssign) -> AssignmentStmt:
        line = n.lineno
        rvalue = self.visit(n.value)
        typ = self.visit(n.annotation)
        assert typ is not None
        s = AssignmentStmt([self.visit(n.target)], rvalue, type_ann=typ)
        return self.set_line(s, n)



    
    def visit_While(self, n: ast3.While) -> WhileStmt:
        node = WhileStmt(
            self.visit(n.test), self.as_required_block(n.body), self.as_block(n.orelse)
        )
        return self.set_line(node, n)

    
    def visit_If(self, n: ast3.If) -> IfStmt:
        node = IfStmt(
            [self.visit(n.test)], [self.as_required_block(n.body)], self.as_block(n.orelse)
        )
        return self.set_line(node, n)


    
    def visit_Assert(self, n: ast3.Assert) -> AssertStmt:
        node = AssertStmt(self.visit(n.test), self.visit(n.msg))
        return self.set_line(node, n)

    
    def visit_Import(self, n: ast3.Import) -> Import:
        names: list[tuple[str, str | None]] = []
        for alias in n.names:
            name = alias.name
            asname = alias.asname
            if asname is None and name != alias.name:
                
                
                
                asname = alias.name
            names.append((name, asname))
        i = Import(names)
        self.imports.append(i)
        return self.set_line(i, n)

    
    def visit_ImportFrom(self, n: ast3.ImportFrom) -> ImportBase:
        assert n.level is not None
        if len(n.names) == 1 and n.names[0].name == "*":
            mod = n.module if n.module is not None else ""
            i: ImportBase = ImportAll(mod, n.level)
        else:
            i = ImportFrom(
                n.module if n.module is not None else "",
                n.level,
                [(a.name, a.asname) for a in n.names],
            )
        self.imports.append(i)
        return self.set_line(i, n)

    
    def visit_Expr(self, n: ast3.Expr) -> ExpressionStmt:
        value = self.visit(n.value)
        node = ExpressionStmt(value)
        return self.set_line(node, n)

    
    def visit_Pass(self, n: ast3.Pass) -> PassStmt:
        s = PassStmt()
        return self.set_line(s, n)

    
    def visit_Break(self, n: ast3.Break) -> BreakStmt:
        s = BreakStmt()
        return self.set_line(s, n)

    
    def visit_Continue(self, n: ast3.Continue) -> ContinueStmt:
        s = ContinueStmt()
        return self.set_line(s, n)

    

    
    def visit_BoolOp(self, n: ast3.BoolOp) -> OpExpr:
        
        assert len(n.values) >= 2
        op_node = n.op
        if isinstance(op_node, ast3.And):
            op = "and"
        elif isinstance(op_node, ast3.Or):
            op = "or"
        else:
            raise RuntimeError("unknown BoolOp " + str(type(n)))

        
        return self.group(op, self.translate_expr_list(n.values), n)

    def group(self, op: str, vals: list[Expression], n: ast3.expr) -> OpExpr:
        if len(vals) == 2:
            e = OpExpr(op, vals[0], vals[1])
        else:
            e = OpExpr(op, vals[0], self.group(op, vals[1:], n))
        return self.set_line(e, n)

    
    def visit_BinOp(self, n: ast3.BinOp) -> OpExpr:
        op = self.from_operator(n.op)

        if op is None:
            raise RuntimeError("cannot translate BinOp " + str(type(n.op)))

        e = OpExpr(op, self.visit(n.left), self.visit(n.right))
        return self.set_line(e, n)

    
    def visit_UnaryOp(self, n: ast3.UnaryOp) -> UnaryExpr:
        op = None
        if isinstance(n.op, ast3.Invert):
            op = "~"
        elif isinstance(n.op, ast3.Not):
            op = "not"
        elif isinstance(n.op, ast3.UAdd):
            op = "+"
        elif isinstance(n.op, ast3.USub):
            op = "-"

        if op is None:
            raise RuntimeError("cannot translate UnaryOp " + str(type(n.op)))

        e = UnaryExpr(op, self.visit(n.operand))
        return self.set_line(e, n)

    
    def visit_IfExp(self, n: ast3.IfExp) -> ConditionalExpr:
        e = ConditionalExpr(self.visit(n.test), self.visit(n.body), self.visit(n.orelse))
        return self.set_line(e, n)

    
    def visit_Dict(self, n: ast3.Dict) -> DictExpr:
        e = DictExpr(
            list(zip(self.translate_opt_expr_list(n.keys), self.translate_expr_list(n.values)))
        )
        return self.set_line(e, n)

    
    def visit_Set(self, n: ast3.Set) -> SetExpr:
        e = SetExpr(self.translate_expr_list(n.elts))
        return self.set_line(e, n)


    
    def visit_Compare(self, n: ast3.Compare) -> ComparisonExpr:
        operators = [self.from_comp_operator(o) for o in n.ops]
        operands = self.translate_expr_list([n.left] + n.comparators)
        e = ComparisonExpr(operators, operands)
        return self.set_line(e, n)

    
    
    def visit_Call(self, n: Call) -> CallExpr:
        args = n.args
        keywords = n.keywords
        keyword_names = [k.arg for k in keywords]
        arg_types = self.translate_expr_list(
            [a.value if isinstance(a, Starred) else a for a in args] + [k.value for k in keywords]
        )
        arg_kinds = [ARG_STAR if type(a) is Starred else ARG_POS for a in args] + [
            ARG_STAR2 if arg is None else ARG_NAMED for arg in keyword_names
        ]
        e = CallExpr(
            self.visit(n.func),
            arg_types,
            arg_kinds,
            cast("List[Optional[str]]", [None] * len(args)) + keyword_names,
        )
        return self.set_line(e, n)

    
    def visit_Constant(self, n: Constant) -> Any:
        val = n.value
        e: Any = None
        if val is None:
            e = NameExpr("None")
        elif isinstance(val, str):
            e = StrExpr(n.s)
        elif isinstance(val, bool):  
            e = NameExpr(str(val))
        elif isinstance(val, int):
            e = IntExpr(val)
        elif isinstance(val, float):
            e = FloatExpr(val)
        elif val is Ellipsis:
            e = EllipsisExpr()
        else:
            raise RuntimeError("Constant not implemented for " + str(type(val)))
        return self.set_line(e, n)

    
    def visit_Num(self, n: ast3.Num) -> IntExpr | FloatExpr:
        
        
        
        
        val: object = n.n
        if isinstance(val, int):
            e: IntExpr | FloatExpr = IntExpr(val)
        elif isinstance(val, float):
            e = FloatExpr(val)
        else:
            raise RuntimeError("num not implemented for " + str(type(val)))
        return self.set_line(e, n)

    
    def visit_Str(self, n: Str) -> StrExpr:
        e = StrExpr(n.s)
        return self.set_line(e, n)

    
    def visit_Ellipsis(self, n: ast3_Ellipsis) -> EllipsisExpr:
        e = EllipsisExpr()
        return self.set_line(e, n)

    
    def visit_Attribute(self, n: Attribute) -> MemberExpr | SuperExpr:
        value = n.value
        member_expr = MemberExpr(self.visit(value), n.attr)
        obj = member_expr.expr
        if (
            isinstance(obj, CallExpr)
            and isinstance(obj.callee, NameExpr)
            and obj.callee.name == "super"
        ):
            e: MemberExpr | SuperExpr = SuperExpr(member_expr.name, obj)
        else:
            e = member_expr
        return self.set_line(e, n)

    
    def visit_Subscript(self, n: ast3.Subscript) -> IndexExpr:
        e = IndexExpr(self.visit(n.value), self.visit(n.slice))
        self.set_line(e, n)
        
        is_py38_or_earlier = sys.version_info < (3, 9)
        if isinstance(n.slice, ast3.Slice) or (
            is_py38_or_earlier and isinstance(n.slice, ast3.ExtSlice)
        ):
            
            
            
            
            e.index.line = e.line
            e.index.column = e.column
        return e


    
    def visit_Name(self, n: Name) -> NameExpr:
        e = NameExpr(n.id)
        return self.set_line(e, n)

    
    def visit_List(self, n: ast3.List) -> ListExpr | TupleExpr:
        expr_list: list[Expression] = [self.visit(e) for e in n.elts]
        if isinstance(n.ctx, ast3.Store):
            
            e: ListExpr | TupleExpr = TupleExpr(expr_list)
        else:
            e = ListExpr(expr_list)
        return self.set_line(e, n)

    
    def visit_Tuple(self, n: ast3.Tuple) -> TupleExpr:
        e = TupleExpr(self.translate_expr_list(n.elts))
        return self.set_line(e, n)

    
    def visit_Index(self, n: Index) -> Node:
        
        value = self.visit(cast(Any, n).value)
        assert isinstance(value, Node)
        return value

def is_possible_trivial_body(s: list[Statement]) -> bool:
    l = len(s)
    if l == 0:
        return False
    i = 0
    if isinstance(s[0], ExpressionStmt) and isinstance(s[0].expr, StrExpr):
        
        i += 1
    if i == l:
        return True
    if l > i + 1:
        return False
    stmt = s[i]
    return isinstance(stmt, PassStmt) or (
        isinstance(stmt, ExpressionStmt) and isinstance(stmt.expr, EllipsisExpr)
    )
