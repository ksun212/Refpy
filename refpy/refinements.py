from dataclasses import dataclass
from typing import Any, List, Dict, Union, Tuple
from refpy.nodes import ConditionalExpr, TypeInfo, ComparisonExpr, CallExpr, Expression, IntExpr, NameExpr, MemberExpr, Block, OpExpr, ReturnStmt, AssignmentStmt, Statement, UnaryExpr
from ast import Attribute, Subscript, expr, IfExp, UnaryOp, Compare, Gt, GtE, Eq, Name, Constant, BinOp, Lt, Add, Sub, Mult, Div, BoolOp, And, FloorDiv
from ast import NodeVisitor as ASTNodeVisitor
from ast import Call as ASTCall

import ast
from refpy.types import (
    Type, FunctionType, ObjectType, AnyType)
import copy

from refpy.visitor import ExpressionVisitor, StatementVisitor, NodeVisitor
var_cnt = -1
pv_cnt = -1
def fresh_var_name():
    global var_cnt
    var_cnt += 1
    return 'v' + str(var_cnt) 

@dataclass(eq=True, frozen=True)
class Refinement:
    self_var: str
    pred: 'list[Expr]'
    def copy_with_new_predicate(self, p):
        return Refinement(self.self_var, p)
@dataclass(eq=True, frozen=True)
class Expr:
    pass
@dataclass(eq=True, frozen=True)
class Variable(Expr):
    var:str
    fields: Tuple = tuple()
    def accept(self, visitor):
        return visitor.visit_variable(self)
    def copy_with_new_var(self, var):
        return Variable(var, self.fields)
    def with_additional_field(self, f):
        return Variable(self.var, self.fields + (f, ))
    def copy_with_view(self, v, to):
        vs = [Variable(self.var)]
        acc = tuple()
        if Variable(self.var, acc) == v:
            left = self.fields
            if isinstance(to, Variable):    
                return mkAttr(to.var, to.fields + left)
            else:
                return to
        for i, f in enumerate(self.fields):
            acc += (f, )
            if Variable(self.var, acc) == v:
                left = self.fields[i+1:]
                if isinstance(to, Variable):    
                    return mkAttr(to.var, to.fields + left)
                else:
                    return to
        return None
    def views(self):
        # each variable can be viewed as multiple variables
        vs = [Variable(self.var)]
        acc = tuple()
        for f in self.fields:
            acc += (f, )
            vs.append(Variable(self.var, acc))
        return vs
@dataclass(eq=True, frozen=True)
class SymConstant(Expr):
    constant:str
    def accept(self, visitor):
        return visitor.visit_sym_constant(self)
@dataclass(eq=True, frozen=True)
class InterpretedConstant(Expr):
    constant:str
    def accept(self, visitor):
        return visitor.visit_interpreted_constant(self)

def mkInterpretedConstant(x):
    return InterpretedConstant(str(x))
@dataclass(eq=True, frozen=True)
class App(Expr):
    func:str
    args:Tuple
    # def __init__(self, x, y):
    #     self.func = x
    #     self.args = y 
    def accept(self, visitor):
        return visitor.visit_app(self)
    def copy_with_new_args(self, args):
        return App(self.func, args)
@dataclass(eq=True, frozen=True)
class Call(Expr):
    callee: Expr
    method:str
    args:Tuple
    callee_class: str = "unset"
    # def __init__(self, x, y):
    #     self.func = x
    #     self.args = y 
    def accept(self, visitor):
        return visitor.visit_call(self)
    def copy_with_new_class(self, c):
        return Call(self.callee, self.method, self.args, c)
@dataclass(eq=True, frozen=True)
class If(Expr):
    cond:Expr
    if_expr:Expr
    else_expr:Expr
    def accept(self, visitor):
        return visitor.visit_if(self)
@dataclass(eq=True, frozen=True)
class Attr(Expr):
    obj:Expr
    field:str
    obj_class: str = "unset"
    def accept(self, visitor):
        return visitor.visit_attr(self)
    def copy_with_new_class(self, c):
        return Attr(self.obj, self.field, c)
    @property
    def fields(self):
        if isinstance(self.obj, Variable):
            return (self.field, )
        else:
            return self.obj.fields + (self.field, )
    def var_name(self):
        if isinstance(self.obj, Variable):
            return self.obj.var
        else:
            return self.obj.var_name()
@dataclass(eq=True, frozen=True)
class BOp:
    op: str
@dataclass(eq=True, frozen=True)
class Bin(Expr):
    op: BOp
    left: Expr
    right: Expr
    def accept(self, visitor):
        return visitor.visit_bin(self)
@dataclass(eq=True, frozen=True)
class Uop(Expr):
    operand: Expr
    def accept(self, visitor):
        return visitor.visit_uop(self)

@dataclass(eq=True, frozen=True)
class Let(Expr):
    vname:str
    e1:Expr
    e2:Expr
    def accept(self, visitor):
        return visitor.visit_let(self)
@dataclass(eq=True, frozen=True)
class Method:
    args: List[str]
    body:Expr

def RelOp(op): 
    return BOp(op)
def Rel(rop, e1, e2): 
    return Bin(rop, e1, e2)
def ConstTrue():
    return InterpretedConstant("true")

def ConsPred(ps, p):
    p1 = copy.deepcopy(ps)
    p1.append(p)
    return p1
    
@dataclass(eq=True, frozen=True)
class RefType:
    base_type: Type
    refinement: Refinement
    def copy_with_new_refinement(self, ref):
        return RefType(self.base_type, ref)
    def copy_with_new_base_type(self, base_type):
        return RefType(base_type, self.refinement)
    
    def __deepcopy__(self, memo):
        return RefType(self.base_type, self.refinement)

    def accept(self, visitor):
        return visitor.visit_ref_type(self)


def mkAttr(name, field_chain):
    return Variable(name, field_chain)

def mkAttr_attr(name, field_chain):
    if len(field_chain) == 1:
        return Attr(name, field_chain[-1])
    else:
        return Attr(mkAttr_attr(name, field_chain[:-1]), field_chain[-1])

vv_ = "v"

def vv():
    return vv_
def relReft(r, e):
    return Refinement(vv_, [Rel(r, Variable(vv_), e)])

def uexprReft(e):
    return relReft(RelOp("="), e)

def mkAdd(v1, v2):
    eq = RelOp("+")
    return Rel(eq, v1, v2)
def mkMin(v1, v2):
    eq = RelOp("-")
    return Rel(eq, v1, v2)
def mkEq(v1, v2):
    bop = BOp("=")
    return Bin(bop, v1, v2)
def mkGe(v1, v2):
    bop = BOp(">=")
    return Bin(bop, v1, v2)
def mkAnd(v1, v2):
    bop = BOp("and")
    return Bin(bop, v1, v2)
def mkNot(v1):
    return Uop(v1)

def mkTrue()->Expr:
    return InterpretedConstant("true")
def mkFalse():
    return InterpretedConstant("false")


def subStr(su:Dict[str, str], x:str):
    if x in su:
        return su[x]
    else:
        return x
    
def printAttr(x:Attr, sp = '.'):
    if isinstance(x.obj, Variable):
        return x.obj.var + sp + x.field
    else:
        return printExpr(x.obj) + sp + x.field
    
def printVar(x, sp = '.'):
    if len(x.fields) > 0:
        return x.var + sp + sp.join(x.fields)
    return x.var
def subVar(su, x:Variable):
    for v in x.views():
        if v in su:
            if isinstance(su[v], Variable):
                return x.copy_with_view(v, su[v])
            else:
                return su[v]
    return x


def subExpr(su: Dict[Variable, Expr], x: Expr):
    if isinstance(x, InterpretedConstant):
        # if x in su:
        #     return su[x]
        # else:
        return x
    if isinstance(x, SymConstant):
        # if x in su:
        #     return su[x]
        # else:
        return x
    if isinstance(x, Variable):
        
        return subVar(su, x)
    if isinstance(x, App):
        # if x in su:
        #     return su[x]
        # else:
        return App(x.func, tuple(subExpr(su, arg) for arg in x.args))
    
    if isinstance(x, Bin):
        return Bin(x.op, subExpr(su, x.left), subExpr(su, x.right))
    
    if isinstance(x, Attr):
        
        return Attr(subExpr(su, x.obj), x.field)
    if isinstance(x, Call):
        return Call(subExpr(su, x.callee), x.method, tuple(subExpr(su, arg) for arg in x.args))
    if isinstance(x, If):
        return If(subExpr(su, x.cond), subExpr(su, x.if_expr), subExpr(su, x.else_expr))
    if isinstance(x, Uop):
        return Uop(subExpr(su, x.operand))
    
    assert False

def subExprs(su: Dict[Variable, Expr], ps: List[Expr]):
    return [(subExpr(su, x)) for x in ps]
def substExcept(su:Dict[Variable, Expr], xs: List[str]):
    su2 = {}
    for k in su:
        if k not in xs:
            su2[k] = su[k]
    return su2
def sub(su:Dict[Variable, Expr], x: Refinement):
    return Refinement(x.self_var, subExprs(substExcept(su, [x.self_var]), x.pred))

def refConjuncts(t: Refinement) -> List[Refinement]:
    return [Refinement(t.self_var, [ra_]) for ra_ in t.pred]


class VarCollector:
    def __init__(self, aim) -> None:
        self.aim = aim
    def visit(self, e) -> List[str]:
        return e.accept(self)
    def visit_forall(self, e):
        return self.visit(e.p)
    def visit_attr(self, e:Attr):
        if self.aim == 'var_dump':
            return self.visit(e.obj)
        elif self.aim == 'var':
            return self.visit(e.obj)
        else:
            return []
    def visit_variable(self, e:Variable):
        if self.aim == 'var_dump':
            return [e]
        elif self.aim == 'var':
            return [e]
        else:
            return []
    def visit_sym_constant(self, e: SymConstant):
        return []
    def visit_interpreted_constant(self, e: InterpretedConstant):
        return []
    def visit_app(self, e: App):
        r:List[str] = []
        for a in e.args:
            r = r + self.visit(a)
        if self.aim == 'carray':
            if e.func == 'IArr':
                return [e] + r
        return r
    def visit_bin(self, p: Bin):
        return self.visit(p.left) + self.visit(p.right)
    def visit_expr(self, p):
        return self.visit(p.expr)
    def visit_rel(self, p):
        return self.visit(p.left) + self.visit(p.right)
    def visit_true(self, p):
        return []
    def visit_false(self, p):
        return []
    def visit_or(self, p):
        return self.visit(p.left) + self.visit(p.right)
    def visit_and(self, p):
        return self.visit(p.left) + self.visit(p.right)
    def visit_not(self, p):
        return self.visit(p.ref)
    def visit_impl(self, p):
        return self.visit(p.left) + self.visit(p.right)
    def visit_bi(self, p):
        return self.visit(p.left) + self.visit(p.right)
    def visit_call(self, p:Call):
        r:List[str] = []
        for a in p.args:
            r = r + self.visit(a)
        return r + self.visit(p.callee)
    
    def visit_if(self, p:If):
        return self.visit(p.cond) + self.visit(p.if_expr) + self.visit(p.else_expr)
    def visit_uop(self, p:Uop):
        return self.visit(p.operand)
    
cv = VarCollector('var')
cd = VarCollector('var_dump')
ca = VarCollector('carray')




def carray_pred(p: Expr):
    return ca.visit(p)

def var_pred(t: Expr):
    return cv.visit(t)

def var_pred_dump(t: Expr):
    names = cd.visit(t)
    
    return names
def printList(ls):
    r = ";".join(str(x) for x in ls)
    r = "[" + r + "]"
    return r
def printExpr(x: Expr):
    if isinstance(x, InterpretedConstant):
        return str(x.constant)
    
    if isinstance(x, SymConstant):
        return x.constant
    
    if isinstance(x, Variable):
        return printVar(x)
    if isinstance(x, Attr):
        return printAttr(x)
    
    if isinstance(x, App):
        return x.func + "(" + printList(printExpr(z) for z in x.args) + ")"
    
    if isinstance(x, Bin):
        return "(" + printExpr(x.left) + ' ' + x.op.op + ' ' + printExpr(x.right) + ")"
    if isinstance(x, Call):
        return "(" + printExpr(x.callee) + '. ' + x.method + "(" + ' ,'.join(printExpr(a) for a in x.args) + ")" + ")"
    
    if isinstance(x, Uop):
        return f"(not {printExpr(x.operand)})"
    if isinstance(x, If):
        return f"(if {printExpr(x.cond)} then {printExpr(x.if_expr)} else {printExpr(x.else_expr)} )"

RelMap = {Gt: ">", Lt: "<", Eq: "=", GtE: ">="}
RelMap2 = {'==': "=", ">=": ">="}
OpMap = {Add: "+", Sub: "-", Mult: "*", Div: "/", FloorDiv: "div"}
PROJ = {0: "fst", 1: "snd", 2: "thd"}
cns = ["Dagger", "Cheese", "Crust", "Pizza", "RemA", "HP", "Cons", "App", "Arrow", "Nil", "FV", "OkType", "NoType", "Bot", "Top", "Zero", "OneMore", "LtdSubV", "ManhattanPt", "OkType", "Z", "S"]
class RefinementT(ASTNodeVisitor):
    def visit_Constant(self, e:Constant) -> Expr:
        if isinstance(e.value, str):
            return SymConstant(e.value)
        elif isinstance(e.value, bool):
            if e.value == True:
                return mkTrue()
            if e.value == False:
                return mkFalse()
            return mkTrue()
        elif isinstance(e.value, int):
            return InterpretedConstant(str(e.value))
        else:
            return mkTrue()
    def visit_Attribute(self, n: Attribute) -> Expr:
        name = self.visit(n.value)
        return mkAttr_attr(name, (n.attr,) )

    def visit_Call(self, e:ASTCall) -> Expr:

        if isinstance(e.func, Name):
            if e.func.id in cns:
                return App(e.func.id+"__Ctor", tuple(self.visit(arg) for arg in e.args))
            return App(e.func.id, tuple(self.visit(arg) for arg in e.args))
        else:
            assert isinstance(e.func, Attribute)
            return Call(self.visit(e.func.value), e.func.attr, tuple(self.visit(arg) for arg in e.args))
    def visit_BinOp(self, node: BinOp) -> Expr:
        op = BOp(OpMap[type(node.op)])
        return Bin(op, self.visit(node.left), self.visit(node.right))
    def visit_Name(self, e:Name) -> Expr:
        if e.id == 'true':
            return mkTrue()
        if e.id == 'True':
            return mkTrue()
        if e.id == 'False':
            return mkTrue()
        return Variable(e.id)
    def visit_Compare(self, e: Compare) -> Expr:
        op = RelOp(RelMap[type(e.ops[0])])
        # if isinstance(e.left, ast.Tuple):
        #     es = []
        #     for i, l in enumerate(e.left.elts):
        #         es.append(Rel(op, self.visit(l), App(PROJ[i], (self.visit(e.comparators[0]), ))))
        #     return mkAnd(es)
        return Rel(op, self.visit(e.left), self.visit(e.comparators[0]))
    def visit_BoolOp(self, node: BoolOp) -> Expr:
        if isinstance(node.op, And):
            assert len(node.values) >= 2
            b = mkAnd(self.visit(node.values[0]), self.visit(node.values[1]))
            for i in range(2, len(node.values)):
                b = mkAnd(b, self.visit(node.values[i]))
            return b
        return mkTrue()
    def visit_UnaryOp(self, node:UnaryOp) -> Expr:
        return mkNot(self.visit(node.operand))
    def visit_IfExp(self, node: IfExp) -> Expr:
        return If(self.visit(node.test), self.visit(node.body), self.visit(node.orelse))
class RefinementTM(NodeVisitor[Expr]):
    def accept_expr(self, expr: Expression):
        
        return expr.accept(self)
    def visit_int_expr(self, e:IntExpr) -> Expr:
        return InterpretedConstant(str(e.value))
    def visit_name_expr(self, o: NameExpr) -> Expr:
        if o.name == 'True':
            return InterpretedConstant('true')
        elif o.name == 'False':
            return InterpretedConstant('false')
        
        return Variable(o.name)
    def visit_op_expr(self, o: OpExpr) -> Expr:
        if o.op == "+":
            return Bin(BOp("+"), self.accept_expr(o.left), self.accept_expr(o.right))
        elif o.op == "-":
            return Bin(BOp("-"), self.accept_expr(o.left), self.accept_expr(o.right))
        elif o.op == "and":
            return Bin(BOp("and"), self.accept_expr(o.left), self.accept_expr(o.right))
        else:
            assert False
    def visit_member_expr(self, o: MemberExpr) -> Expr:
        return Attr(self.accept_expr(o.expr), o.name)
    def visit_call_expr(self, o: CallExpr) -> Expr:
        if isinstance(o.callee, MemberExpr):
            return Call(self.accept_expr(o.callee.expr), o.callee.name, tuple(self.accept_expr(arg) for arg in o.args))
        elif isinstance(o.callee, NameExpr):
            if isinstance(o.callee.node, TypeInfo):
                return App(o.callee.name + "__Ctor", tuple(self.accept_expr(arg) for arg in o.args))
            return App(o.callee.name, tuple(self.accept_expr(arg) for arg in o.args))
        else:
            assert False
    def visit_comparison_expr(self, e: ComparisonExpr) -> Expr:
        op = RelOp(RelMap2[e.operators[0]])
        return Rel(op, self.accept_expr(e.operands[0]), self.accept_expr(e.operands[1]))    
    def visit_conditional_expr(self, o: ConditionalExpr) -> Expr:
        return If(self.accept_expr(o.cond), self.accept_expr(o.if_expr), self.accept_expr(o.else_expr))
    def visit_unary_expr(self, o: UnaryExpr) -> Expr:
        return Uop(self.accept_expr(o.expr))
def transform_refinement(node:expr) -> list[Expr]:
    assert isinstance(node, Subscript) and isinstance(node.value, Name) and node.value.id == 'Ref'
    node = node.slice
    assert isinstance(node, Subscript)
    if isinstance(node.slice, Subscript): # Generic Type
        node = node.slice
    refinement_transformer = RefinementT()
    pred = refinement_transformer.visit(node.slice)
    return [pred]
def transform_refinement_v(node:Expression) -> Expr:
    # Expression to predicate, can also be defined via translation to expr then to predicate
    refinement_transformer = RefinementTM()
    pred = node.accept(refinement_transformer)
    return pred

def transform_let(node:List[Statement]) -> Expr:
    if len(node) == 1:
        assert isinstance(node[0], ReturnStmt) and node[0].expr
        return transform_refinement_v(node[0].expr)
    else:
        assert isinstance(node[0], AssignmentStmt) and isinstance(node[0].lvalues[0], NameExpr)
        return Let(node[0].lvalues[0].name, transform_refinement_v(node[0].rvalue), transform_let(node[1:]))
    
def selfication(t: RefType, x: Expr) -> RefType:
    new_ref = t.refinement.copy_with_new_predicate(ConsPred(t.refinement.pred, mkEq(Variable(t.refinement.self_var), x)))
    return t.copy_with_new_refinement(new_ref)


def strengthen(t: RefType, x: Expr) -> RefType:
    new_ref = t.refinement.copy_with_new_predicate(ConsPred(t.refinement.pred, x))
    return t.copy_with_new_refinement(new_ref)
def trivalRf():
    return Refinement(vv(), [mkTrue()])
def trivalRef(t):
    return RefType(t, trivalRf())
