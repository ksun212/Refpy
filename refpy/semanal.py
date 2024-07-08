from __future__ import annotations
from typing import List, TypeVar
from refpy.refinements import RefType, Refinement, trivalRef, vv
from refpy.errors import ErrorCollectors
from refpy.nodes import (
    AssertStmt,
    AssignmentStmt,
    Block,
    BreakStmt,
    CallExpr,
    ClassDef,
    ComparisonExpr,
    ConditionalExpr,
    Context,
    ContinueStmt,
    DictExpr,
    Expression,
    ExpressionStmt,
    FuncDef,
    IfStmt,
    IndexExpr,
    ListExpr,
    Lvalue,
    MemberExpr,
    RefpyFile,
    NameExpr,
    Node,
    OpExpr,
    RefExpr,
    ReturnStmt,
    SetExpr,
    StrExpr,
    SuperExpr,
    SymbolNode,
    SymbolTable,
    TupleExpr,
    TypeInfo,
    UnaryExpr,
    Var,
    WhileStmt,
)
from refpy.options import Options
from refpy.types import FunctionStub, FunctionType, ObjectType, Type
from refpy.visitor import NodeVisitor

T = TypeVar("T")

class SymboBinder(NodeVisitor[None]):

    modules: dict[str, RefpyFile]
    global_table: SymbolTable
    local_tables: list[SymbolTable | None]
    current_class: TypeInfo | None = None
    options: Options
    loop_depth: list[int]
    errors: ErrorCollectors

    def __init__(self, modules: dict[str, RefpyFile], errors: ErrorCollectors, options: Options) -> None:
        self.local_tables = [None]
        self.current_class = None
        self.loop_depth = [0]
        self.errors = errors
        self.modules = modules
        self.options = options

    @property
    def type(self) -> TypeInfo | None:
        return self.current_class
    
    def begin(self,  file_node: RefpyFile) -> None:
        self.errors.set_file(file_node.path, file_node.fullname, options=self.options)
        for d in file_node.defs:
            self.accept(d)


    def visit_func_def(self, defn: FuncDef) -> None:

        for arg in defn.arguments:
            if arg.initializer:
                arg.initializer.accept(self)

        self.analyze_func_def(defn)

    def analyze_func_def(self, defn: FuncDef) -> None:
        if defn.type:
            assert isinstance(defn.type, FunctionStub)
            t = defn.type
            at = [self.expr_to_type(e) for e in t.arg_types if isinstance(e, Expression)]
            assert isinstance(t.ret_type, Expression)
            rt = self.expr_to_type(t.ret_type)
            rat = [Refinement(vv(), p) for p in t.ref_arg_types]
            rrt = Refinement(vv(), t.ref_ret_type)
            defn.ref_type = FunctionType(at, t.arg_kinds, t.arg_names, rt, t.name, t.definition, t.line, t.column, rat, rrt)

        self.analyze_function_body(defn)

    def analyze_arg_initializers(self, defn: FuncDef) -> None:
        for arg in defn.arguments:
            if arg.initializer:
                arg.initializer.accept(self)

    def analyze_function_body(self, defn: FuncDef) -> None:
        self.local_tables.append(dict())
        self.loop_depth.append(0)
        for arg in defn.arguments:
            self.add_local(arg.variable)
        defn.body.accept(self)
        self.local_tables.pop()
        self.loop_depth.pop()

    def visit_class_def(self, defn: ClassDef) -> None:
        bases = defn.base_type_exprs
        assert defn.info
        if defn.fullname == "builtins.object":
            defn.info.base = defn.info
            defn.info.bases = [defn.info]
        else:
            if len(bases) > 0:
                base = self.expr_to_type(bases[0])
                assert isinstance(base, ObjectType)
            else:
                base = self.named_type("builtins.object")
            bi = base.type
            defn.info.base = bi
            defn.info.bases = self.get_bases(defn.info)
        self.local_tables.append(None)
        self.loop_depth.append(0)
        self.current_class = defn.info
        defn.defs.accept(self)
        self.loop_depth.pop()
        self.local_tables.pop()

    def get_bases(self, base: TypeInfo) -> List[TypeInfo]:
        if base.fullname == "builtins.object":
            return [base]
        else:
            return [base] + self.get_bases(base.base)

    def visit_assignment_stmt(self, s: AssignmentStmt) -> None:
        if s.rvalue:
            s.rvalue.accept(self)
        self.check_annotation(s)

    def check_annotation(self, s: AssignmentStmt) -> None:
        if s.type_ann:
            lvalue = s.lvalues[-1]
            t = self.expr_to_type(s.type_ann)
            if t:
                s.type = t
                for lvalue in s.lvalues:
                    if isinstance(lvalue, RefExpr):
                        if isinstance(lvalue.node, Var):
                            var = lvalue.node
                            var.type = t
                            if s.ref_type:
                                var.ref_type = RefType(t, Refinement(vv(), s.ref_type))
                            else:
                                var.ref_type = trivalRef(t)

    def visit_block(self, b: Block) -> None:
        for s in b.body:
            self.accept(s)

    def visit_block_maybe(self, b: Block | None) -> None:
        if b:
            self.visit_block(b)

    def visit_expression_stmt(self, s: ExpressionStmt) -> None:
        s.expr.accept(self)

    def visit_return_stmt(self, s: ReturnStmt) -> None:
        if not self.is_func_scope():
            self.errors.report(s.line, s.column, '"return" outside function')
        if s.expr:
            s.expr.accept(self)

    def visit_assert_stmt(self, s: AssertStmt) -> None:
        if s.expr:
            s.expr.accept(self)
        if s.msg:
            s.msg.accept(self)

    def visit_while_stmt(self, s: WhileStmt) -> None:
        s.expr.accept(self)
        self.loop_depth[-1] += 1
        s.body.accept(self)
        self.loop_depth[-1] -= 1
        self.visit_block_maybe(s.else_body)

    def visit_break_stmt(self, s: BreakStmt) -> None:
        if self.loop_depth[-1] == 0:
            self.errors.report(s.line, s.column, '"break" outside loop')

    def visit_continue_stmt(self, s: ContinueStmt) -> None:
        if self.loop_depth[-1] == 0:
            self.errors.report(s.line, s.column, '"continue" outside loop')

    def visit_if_stmt(self, s: IfStmt) -> None:
        for i in range(len(s.expr)):
            s.expr[i].accept(self)
            self.visit_block(s.body[i])
        self.visit_block_maybe(s.else_body)

    
    def visit_name_expr(self, expr: NameExpr) -> None:
        sym = self.lookup(expr.name)
        if sym:
            expr.node = sym
            expr.fullname = sym.fullname or ""

    def visit_super_expr(self, expr: SuperExpr) -> None:
        if not self.type and not expr.call.args:
            self.errors.report(expr.line, expr.column, '"super" used outside class')
            return
        expr.info = self.type
        for arg in expr.call.args:
            arg.accept(self)

    def visit_tuple_expr(self, expr: TupleExpr) -> None:
        for item in expr.items:
            item.accept(self)

    def visit_list_expr(self, expr: ListExpr) -> None:
        for item in expr.items:
            item.accept(self)

    def visit_set_expr(self, expr: SetExpr) -> None:
        for item in expr.items:
            item.accept(self)

    def visit_dict_expr(self, expr: DictExpr) -> None:
        for key, value in expr.items:
            if key is not None:
                key.accept(self)
            value.accept(self)
    def visit_call_expr(self, expr: CallExpr) -> None:
        
        expr.callee.accept(self)
        for a in expr.args:
            a.accept(self)

    def visit_member_expr(self, expr: MemberExpr) -> None:
        base = expr.expr
        base.accept(self)
        if isinstance(base, RefExpr) and isinstance(base.node, RefpyFile):
            sym = self.get_module_symbol(base.node, expr.name)
            if sym:
                expr.fullname = sym.fullname or ""
                expr.node = sym
        elif isinstance(base, RefExpr):
            type_info = None
            if isinstance(base.node, TypeInfo):
                type_info = base.node

            if type_info:
                n = type_info.names.get(expr.name)
                if n is not None and isinstance(n, (RefpyFile, TypeInfo)):
                    if not n:
                        return
                    expr.fullname = n.fullname or ""
                    expr.node = n

    def visit_op_expr(self, expr: OpExpr) -> None:
        expr.left.accept(self)
        expr.right.accept(self)

    def visit_comparison_expr(self, expr: ComparisonExpr) -> None:
        for operand in expr.operands:
            operand.accept(self)

    def visit_unary_expr(self, expr: UnaryExpr) -> None:
        expr.expr.accept(self)

    def visit_index_expr(self, expr: IndexExpr) -> None:
        base = expr.base
        base.accept(self)
        expr.index.accept(self)

    def visit_conditional_expr(self, expr: ConditionalExpr) -> None:
        expr.if_expr.accept(self)
        expr.cond.accept(self)
        expr.else_expr.accept(self)

    def lookup(self, name: str) -> SymbolNode | None:
        if self.type and not self.is_func_scope() and name in self.type.names:
            node = self.type.names[name]
            return node
        for table in reversed(self.local_tables):
            if table is not None and name in table:
                return table[name]
        if name in self.global_table:
            return self.global_table[name]
        b = self.global_table.get("__builtins__", None)
        if b:
            assert isinstance(b, RefpyFile)
            table = b.names
            if name in table:
                node = table[name]
                return node

        return None

    def get_module_symbol(self, node: RefpyFile, name: str) -> SymbolNode | None:
        module = node.fullname
        names = node.names
        sym = names.get(name)
        if not sym:
            fullname = module + "." + name
            if fullname in self.modules:
                sym = self.modules[fullname]
        return sym
    def lookup_fully_qualified(self, fullname: str) -> SymbolNode|None:
        assert "." in fullname
        module, name = fullname.rsplit(".", maxsplit=1)
        if module not in self.modules:
            return None
        filenode = self.modules[module]
        result = filenode.names.get(name)
        return result

    def named_type(self, fullname: str) -> ObjectType:
        sym = self.lookup_fully_qualified(fullname)
        assert sym, "Internal error: attempted to construct unknown type"
        node = sym
        assert isinstance(node, TypeInfo)
        return ObjectType(node)

    def add_local(self, node: Var) -> None:
        
        assert self.is_func_scope()
        name = node.name
        node._fullname = name

        assert self.local_tables[-1] is not None
        names = self.local_tables[-1]
        symbol =  node
        names[name] = symbol

    def is_func_scope(self) -> bool:
        return self.local_tables[-1] is not None

    def accept(self, node: Node) -> None:
        node.accept(self)

    def expr_to_type(self,node: Expression) -> Type:
        assert isinstance(node, (NameExpr, StrExpr))
        if isinstance(node, NameExpr):
            name = node.name
        else:
            name = node.value
        if name in ["True", "False"]:
            bl_info = self.lookup_fully_qualified("builtins.bool")
        else:
            bl_info = self.lookup(name)
        assert isinstance(bl_info, TypeInfo)
        return ObjectType(bl_info)

