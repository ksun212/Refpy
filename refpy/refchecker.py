

from __future__ import annotations

from typing import Dict, List, Tuple
from copy import  deepcopy
from refpy.errors import ErrorCollectors
from refpy.ref_solver import RefSolver
from refpy.nodes import (
    ARG_POS,
    AssignmentStmt,
    Block,
    CallExpr,
    ClassDef,
    ComparisonExpr,
    Expression,
    FuncDef,
    ImportFrom,
    IntExpr,
    MemberExpr,
    RefpyFile,
    NameExpr,
    OpExpr,
    PassStmt,
    ReturnStmt,
    Statement,
    StrExpr,
    ConditionalExpr,
    SymbolNode,
    TypeInfo,
    UnaryExpr,
)
from refpy.options import Options
from dataclasses import dataclass
from refpy.refinements import transform_refinement_v, trivalRf, SymConstant, mkAttr_attr, InterpretedConstant, strengthen, selfication, SymConstant, mkAnd, mkNot, Variable, vv, uexprReft, refConjuncts, RefType, Refinement, fresh_var_name, mkEq, mkGe, mkAdd, mkMin, mkTrue, sub
from refpy.smt import SMTInterface

from refpy.types import FunctionType,  ObjectType, Type

from refpy.visitor import NodeVisitor

@dataclass
class Env:
    type_map: Dict[str, RefType]
    id_map: Dict[str, int]
@dataclass
class SubC:
    senv: Env
    slhs: RefType
    srhs: RefType
    line: int

@dataclass
class SMTSubC:
    _senv: set[int]
    slhs: RefType
    srhs: RefType
    line: int
    def copy_with_new_slhs(self, slhs):
        return SMTSubC(self._senv, slhs, self.srhs, self.line)
    def copy_with_new_srhs(self, srhs):
        return SMTSubC(self._senv, self.slhs, srhs, self.line)

@dataclass
class CheckInfo:
    subs: List[SMTSubC]
    bs: Dict[int, Tuple[str, RefType]] 

# Env, 
def subC(ib, sr1, sr2:RefType, line):
    return [SMTSubC(ib, sr1, RefType(sr2.base_type, sr2_), line) for sr2_ in refConjuncts(sr2.refinement)]
class RefChecker(NodeVisitor[RefType]):
    def __init__(
        self,
        modules: dict[str, RefpyFile],
        options: Options,
        tree: RefpyFile,
        path: str,
        errors: ErrorCollectors, 
    ) -> None:
        self.modules = modules
        self.options = options
        self.tree = tree
        self.path = path
        self.globals = tree.names
        self.binds:Dict[int, Tuple[str, RefType]] = {}
        self.var_num = 0
        self.cs:list[SubC] = []
        self.cs_stack:list[list[SubC]] = []
        self.smt = SMTInterface(self)
        self.solver = RefSolver()
        self.args:set[str] = set()
        self.su:dict = {}
        self.slience = False
        self.errors = errors
        self.g: Env = Env({}, {})
        self.object_type = RefType(self.named_type("object"), Refinement("v", [mkTrue()]))
        self.class_defs:List[ClassDef] = []
    def bsplitC_(self, g:Env, t1, t2, line):
        r1 = t1
        r2 = t2
        # there may be multiple variables in the environment, get the visable scope of those variables. 
        id_list = g.id_map.values()
        bs = set()
        for id_ in id_list:
            bs.add(id_)
        return subC(bs, r1, r2, line)
    def bsplitC(self, g:Env, t1, t2, line) -> List[SubC]:
        return self.bsplitC_(g, t1, t2, line)
    # SubC to SMTSubC
    def splitC(self, c: SubC):
        
        cs = self.bsplitC(c.senv, c.slhs, c.srhs, c.line)
        # no type constructor now
        return cs

            
    def toCInfo(self, local = False) -> CheckInfo:
        bs = self.binds
        fcs = []
        if local:
            for c in self.cs_stack[-1]:
                fcs.extend(self.splitC(c))
        else:
            for c in self.cs:
                fcs.extend(self.splitC(c))
        return CheckInfo(fcs, bs)
    
    def insertBindEnv(self, x, r, bs:Dict[int, Tuple[str, RefType]]):
        bs[self.var_num] = (x, r)
        self.var_num += 1
        return self.var_num - 1, bs
    def addBind(self, x, e) -> int:
        bs = self.binds
        r = e
        i, bs_ = self.insertBindEnv(x, r, bs)
        self.binds = bs_
        return i
    def envAdds(self, xts:List[tuple[str, RefType]], g):
        xs = [x[0] for x in xts]
        ts = [x[1] for x in xts]
        ids = [self.addBind(x, e) for x, e in zip(xs, ts)]
        g = deepcopy(g)
        for x, t, id_ in zip(xs, ts, ids):
            g.type_map[x] = t
            g.id_map[x] = id_
        return g
    def check_first_pass(self) -> None:
        self.recurse_into_functions = True
        self.cs_stack.append([])
        
        # Init env
        for d in self.tree.defs:
            if isinstance(d, FuncDef):
                g = self.add_func_type(d)
            if isinstance(d, ClassDef):
                g = self.add_class_type(d)
        for d in self.tree.defs:
            _ = self.accept_stmt(d)
        
        cInfo = self.toCInfo()
        worklist = self.solver.check(cInfo)
        class_defs = [x for x in self.tree.defs if isinstance (x, ClassDef)]
        self.class_defs.extend(class_defs)
        self.smt.write(worklist, self.class_defs)
        self.cs_stack.pop()
        



    def accept_stmt(self, stmt: Statement) -> RefType:
        return stmt.accept(self)
    def accept_expr(self, expr: Expression) -> RefType:
        return expr.accept(self)

    # 
    # Expressions
    # 

    def subtype(self, g, t1, t2, line):
        self.cs.append(SubC(deepcopy(g), t1, t2, line))
        self.cs_stack[-1].append(SubC(deepcopy(g), t1, t2, line))
        
    def visit_import_from(self, node: ImportFrom) -> RefType:
        for d in self.modules[node.id].defs:
            if isinstance(d, ClassDef):
                self.class_defs.append(d)
        return self.visit_int_expr(IntExpr(0))
    def visit_bool_expr(self, e: str):
        typ = self.named_type("builtins.bool")
        return RefType(typ, uexprReft(InterpretedConstant(str(e))))
    def visit_int_expr(self, e: IntExpr):
        typ = self.named_type("builtins.int")
        return RefType(typ, uexprReft(InterpretedConstant(str(e.value))))
    def visit_str_expr(self, e: StrExpr):
        typ = self.named_type("builtins.str")
        return RefType(typ, uexprReft(SymConstant(str(e.value))))
    
    def visit_conditional_expr(self, e: ConditionalExpr):
        t = self.accept_expr(e.cond)
        orig = self.g
        g1 = self.envAdds([("cond", selfication(t, transform_refinement_v(e.cond)))], deepcopy(orig))
        self.g = g1
        t1 = self.accept_expr(e.if_expr)
        g2 = self.envAdds([("cond", selfication(t, mkNot(transform_refinement_v(e.cond))))], deepcopy(orig))
        self.g = g2
        t2 = self.accept_expr(e.else_expr)
        self.g = orig
        # assume t1 = t2
        return selfication(t2, transform_refinement_v(e))

    def subst(self, su, ref:Refinement):
        return sub(su, ref)

    def visit_call_expr(self, e: CallExpr):
        ts = []
        names = []
        t = self.accept_expr(e.callee)
        retic_type = t.base_type
        assert isinstance(retic_type, FunctionType)
        if isinstance(e.callee, MemberExpr):
            for i in range(len(e.args)):
                arg = e.args[i]
                t = self.accept_expr(arg)
                ts.append(t)
                names.append(arg)
            t = self.accept_expr(e.callee.expr) # <Assume> x.f
            ts = [t] + ts
            names.insert(0, e.callee.expr)
        else:
            for i in range(len(e.args)):
                arg = e.args[i]
                t = self.accept_expr(arg)
                ts.append(t)
                names.append(arg)
        
        rt = self.check_apply(self.g, retic_type, names, ts)
        return selfication(rt, transform_refinement_v(e))
    def check_apply(self, g:Env, func_type:FunctionType, es, xts):
        
        yts = [(arg, t) for arg, t in zip(func_type.arg_names, func_type.ref_arg_types)] 
        su = {Variable(y[0]):transform_refinement_v(e) for y, e in zip(yts, es) if isinstance(y[0], str)}
        t_rf = func_type.ref_ret_type
        a_rf = [x for x in func_type.ref_arg_types]
        t_rf2 = self.subst(su, t_rf)
        a_rf2 = [self.subst(su, a) for a in a_rf]
        t2 = RefType(func_type.ret_type, t_rf2)
        a2 = [RefType(a, a_r) for a, a_r in zip(func_type.arg_types, a_rf2)]
        for i, (arg, param) in enumerate(zip(xts, a2)):
            line = es[i].line
            if not self.slience:
                self.subtype(g, arg, param, line)
        # subst
        return t2
    def visit_unary_expr(self, e:UnaryExpr):
        
        t1 = self.accept_expr(e.expr)
        name1 = fresh_var_name()
        name2 = vv()
        arg1_type_ = self.named_type("builtins.bool")
        arg1_type = Refinement(name1, [mkTrue()])
        ret_ref = Refinement(name2, [mkEq(Variable(name2), mkNot(Variable(name1)))])
        ret_type_ = self.named_type("builtins.bool")
        ret_type = ret_ref
        retic_type = FunctionType([arg1_type_], [ARG_POS], [name1], ret_type_, ref_arg_types=[arg1_type], ref_ret_type=ret_type)
        return self.check_apply(self.g, retic_type, [e.expr], [t1])
    def visit_name_expr(self, e: NameExpr):
        if e.name in ['True', 'False', 'builtins.True' 'builtins.False']:
            return self.visit_bool_expr(e.name.lower())
        
        t = selfication(self.g.type_map[e.name], Variable(e.name))
        return t 
    def visit_op_expr(self, e: OpExpr) -> RefType:
        "+, -, and"
        result: Type | None = None
        sub_result: Type
        if e.op == "+":
            t1 = self.accept_expr(e.left)
            t2 = self.accept_expr(e.right)
            
            name1 = fresh_var_name()
            name2 = fresh_var_name()
            name3 = vv()
            arg1_type_ = self.named_type("builtins.int")
            arg1_type = Refinement(name1, [mkTrue()])
            arg2_type_ = self.named_type("builtins.int")
            arg2_type = Refinement(name2, [mkTrue()])
            ret_ref = Refinement(name3, [mkEq(Variable(name3), mkAdd(Variable(name1), Variable(name2)))])
            ret_type_ = self.named_type("builtins.int")
            ret_type = ret_ref
            retic_type = FunctionType([arg1_type_, arg2_type_], [ARG_POS, ARG_POS], [name1, name2], ret_type_, ref_arg_types=[arg1_type, arg2_type], ref_ret_type=ret_type)
            return self.check_apply(self.g, retic_type, [e.left, e.right], [t1, t2])
        elif e.op == "-":
            t1 = self.accept_expr(e.left)
            t2 = self.accept_expr(e.right)
            
            name1 = fresh_var_name()
            name2 = fresh_var_name()
            name3 = vv()
            arg1_type_ = self.named_type("builtins.int")
            arg1_type = Refinement(name1, [mkTrue()])
            arg2_type_ = self.named_type("builtins.int")
            arg2_type = Refinement(name2, [mkTrue()])
            ret_ref = Refinement(name3, [mkEq(Variable(name3), mkMin(Variable(name1), Variable(name2)))])
            ret_type_ = self.named_type("builtins.int")
            ret_type = ret_ref
            retic_type = FunctionType([arg1_type_, arg2_type_], [ARG_POS, ARG_POS], [name1, name2], ret_type_, ref_arg_types=[arg1_type, arg2_type], ref_ret_type=ret_type)
            return self.check_apply(self.g, retic_type, [e.left, e.right], [t1, t2])
        else:
            t1 = self.accept_expr(e.left)
            t2 = self.accept_expr(e.right)
            
            name1 = fresh_var_name()
            name2 = fresh_var_name()
            name3 = vv()
            arg1_type_ = self.named_type("builtins.int")
            arg1_type = Refinement(name1, [mkTrue()])
            arg2_type_ = self.named_type("builtins.int")
            arg2_type = Refinement(name2, [mkTrue()])
            ret_ref = Refinement(name3, [mkEq(Variable(name3), mkAnd(Variable(name1), Variable(name2)))])
            ret_type_ = self.named_type("builtins.bool")
            ret_type = ret_ref
            retic_type = FunctionType([arg1_type_, arg2_type_], [ARG_POS, ARG_POS], [name1, name2], ret_type_, ref_arg_types=[arg1_type, arg2_type], ref_ret_type=ret_type)
            return self.check_apply(self.g, retic_type, [e.left, e.right], [t1, t2])
    def visit_comparison_expr(self, e: ComparisonExpr) -> RefType:
        "="
        result: Type | None = None
        sub_result: Type
        assert len(e.operators) == 1
        assert len(e.operands) == 2
        if e.operators[0] == '==':
            t1 = self.accept_expr(e.operands[0])
            t2 = self.accept_expr(e.operands[1])
            
            name1 = fresh_var_name()
            name2 = fresh_var_name()
            name3 = vv()
            
            arg1_type_ = self.named_type("builtins.int")
            arg1_type = Refinement(name1, [mkTrue()])
            arg2_type_ = self.named_type("builtins.int")
            arg2_type = Refinement(name2, [mkTrue()])
            ret_ref = Refinement(name3, [mkEq(Variable(name3), mkEq(Variable(name1), Variable(name2)))])
            ret_type_ = self.named_type("builtins.bool")
            ret_type = ret_ref
            retic_type = FunctionType([arg1_type_, arg2_type_], [ARG_POS, ARG_POS], [name1, name2], ret_type_, ref_arg_types=[arg1_type, arg2_type], ref_ret_type=ret_type)
            return self.check_apply(self.g, retic_type, e.operands, [t1, t2])
        else:
            t1 = self.accept_expr(e.operands[0])
            t2 = self.accept_expr(e.operands[1])
            
            name1 = fresh_var_name()
            name2 = fresh_var_name()
            name3 = vv()
            arg1_type_ = self.named_type("builtins.int")
            arg1_type = Refinement(name1, [mkTrue()])
            arg2_type_ = self.named_type("builtins.int")
            arg2_type = Refinement(name2, [mkTrue()])
            ret_ref = Refinement(name3, [mkEq(Variable(name3), mkGe(Variable(name1), Variable(name2)))])
            ret_type_ = self.named_type("builtins.bool")
            ret_type = ret_ref
            retic_type = FunctionType([arg1_type_, arg2_type_], [ARG_POS, ARG_POS], [name1, name2], ret_type_, ref_arg_types=[arg1_type, arg2_type], ref_ret_type=ret_type)
            return self.check_apply(self.g, retic_type, e.operands, [t1, t2])
        # Check each consecutive operand pair and their operator
        
    #
    # Definitions
    #


    def add_func_type(self, defn: FuncDef) -> Env:

        self.g.type_map[defn.name] = defn.ref_type
        return self.g
    def add_class_type(self, c: ClassDef) -> Env:
        rt = self.getProp(c.info, "__init__")
        self.g.type_map[c.name] = rt
        return self.g

    def getProp(self, info, f):
        for n in info.bases:
            if f in n.names:
                node = n.names[f]
                if isinstance(node, FuncDef):
                    if node.name == '__init__':
                        ref_func = node.ref_type
                        selfed_ref_func = FunctionType(ref_func.arg_types[1:], ref_func.arg_kinds[1:], ref_func.arg_names[1:], ref_func.ret_type, None, ref_arg_types=ref_func.ref_arg_types[1:] if ref_func.ref_arg_types else None, ref_ret_type=ref_func.ref_ret_type)
                        return RefType(selfed_ref_func, trivalRf())
                    else:
                        return RefType(node.ref_type, trivalRf())
                else:
                    return node.ref_type
    def getProp_node(self, info, f):
        for n in info.bases:
            if f in n.names:
                node = n.names[f]
                return node
    
    def visit_member_expr(self, mem: MemberExpr):
        t = self.accept_expr(mem.expr)
        assert isinstance(t.base_type, ObjectType)
        t2 = self.getProp(t.base_type.type, mem.name)
        su = {Variable("self"):transform_refinement_v(mem.expr)}
        t2f = self.subst(su, t2.refinement)
        t2 = t2.copy_with_new_refinement(t2f)
        return selfication(t2, mkAttr_attr(transform_refinement_v(mem.expr), (mem.name, )))

    def visit_class_def(self, clas: ClassDef) -> RefType:
        for d in clas.defs.body:
            if isinstance(d, FuncDef):
                # if is constructor
                if d.name == '__init__':
                    pass # skip checking constructor
                # if is member method
                else:
                    _ = self.visit_func_def(d)
        return self.object_type
    
    def visit_func_def(self, defn: FuncDef) -> RefType:
        # we need to ensure the two predicate variables are generated and eliminated. 
        self.cs_stack.append([])
        assert isinstance(defn.ref_type, FunctionType)
        arg_types = [RefType(t,r) for t,r in zip(defn.ref_type.arg_types, defn.ref_type.ref_arg_types)]
        ret_type = RefType(defn.ref_type.ret_type, defn.ref_type.ref_ret_type)
        entry_to_add = [(n, t) for n, t in zip(defn.ref_type.arg_names, arg_types) if isinstance(n, str)]
        orig = self.g
        self.g = self.envAdds(entry_to_add, deepcopy(self.g))
        self.ret_type = ret_type
        _ = self.accept_stmt(defn.body)
        stub = len(defn.body.body) == 1 and isinstance(defn.body.body[0], PassStmt)
        # inplace update
        new_arg_types = arg_types # self.substi_arg_types(su, arg_types)
        new_ret_type = ret_type # self.substi_ret_type(su, ret_type)
        self.cs_stack.pop()
        self.g = orig
        return new_ret_type
    def visit_pass_stmt(self, r: PassStmt) -> RefType:
        return self.object_type
    def visit_return_stmt(self, r: ReturnStmt) -> RefType:

        # special case for return if-then-else, since we need to checking instead of synthesis to achieve flow-sensitive value not only flow sensitive checking
        if isinstance(r.expr, ConditionalExpr):
            e = r.expr
            t = self.accept_expr(e.cond)
            orig = self.g
            self.g = self.envAdds([("cond", strengthen(t, mkEq(transform_refinement_v(e.cond), mkTrue())))], deepcopy(orig))
            
            t1 = self.accept_expr(e.if_expr)
            self.subtype(self.g, t1, self.ret_type, r.line)
            self.g = self.envAdds([("cond", strengthen(t, mkEq(mkNot(transform_refinement_v(e.cond)), mkTrue())))], deepcopy(orig))
            t2 = self.accept_expr(e.else_expr)
            self.subtype(self.g, t2, self.ret_type, r.line)
            return t2
        else:
            assert r.expr
            t = self.accept_expr(r.expr)
            self.subtype(self.g, t, self.ret_type, r.line)
            return t


    #
    # Statements
    #

    def visit_block(self, b: Block) -> RefType:
        for s in b.body:
            g = self.accept_stmt(s)
        return g

    def visit_assignment_stmt(self, s: AssignmentStmt) -> RefType:
        if len(s.lvalues) == 1:
            if isinstance(s.lvalues[0], NameExpr):
                t = self.accept_expr(s.rvalue)
                self.g = self.envAdds([(s.lvalues[0].name, t)], self.g)
                return t
        return self.object_type
    def named_type(self, name: str) -> ObjectType:
        # Assume that the name refers to a type.
        sym = self.lookup_qualified(name)
        node = sym
        assert isinstance(node, TypeInfo)
        return ObjectType(node)
 

    def lookup_typeinfo(self, fullname: str) -> TypeInfo:
        # Assume that the name refers to a class.
        sym = self.lookup_qualified(fullname)
        node = sym
        assert isinstance(node, TypeInfo)
        return node

    def type_type(self) -> ObjectType:
        return self.named_type("builtins.type")

    def str_type(self) -> ObjectType:
        return self.named_type("builtins.str")



    def lookup(self, name: str) -> SymbolNode:
        if name in self.globals:
            return self.globals[name]
        else:
            b = self.globals.get("__builtins__", None)
            if b:
                assert isinstance(b, RefpyFile)
                table = b.names
                if name in table:
                    return table[name]
            raise KeyError(f"Failed lookup: {name}")

    def lookup_qualified(self, name: str) -> SymbolNode:
        if "." not in name:
            return self.lookup(name)
        else:
            parts = name.split(".")
            n = self.modules[parts[0]]
            for i in range(1, len(parts) - 1):
                sym = n.names.get(parts[i])
                assert sym is not None, "Internal error: attempted lookup of unknown name"
                assert isinstance(sym, RefpyFile)
                n = sym
            last = parts[-1]
            if last in n.names:
                return n.names[last]
            elif len(parts) == 2 and parts[0] in ("builtins", "typing"):
                fullname = ".".join(parts)
                suggestion = ""
                raise KeyError(
                    "Could not find builtin symbol '{}' (If you are running a "
                    "test case, use a fixture that "
                    "defines this symbol{})".format(last, suggestion)
                )
            else:
                msg = "Failed qualified lookup: '{}' (fullname = '{}')."
                raise KeyError(msg.format(last, name))
