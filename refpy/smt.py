import subprocess
import copy
import os
from refpy.ref_solver import VC
from refpy.refinements import printExpr, Uop, If, Let, transform_let, carray_pred, var_pred_dump, Variable, Attr, Expr, InterpretedConstant, SymConstant, printVar, App, Bin, Call
from typing import List, Set
from refpy.nodes import ClassDef, FuncDef, PassStmt, TypeInfo, Var
from refpy.types import Type, FunctionType, ObjectType
def cons(mp, x, t):
    mp_ = copy.copy(mp)
    mp_[x] = t
    return mp_
class SMTInterface:
    def __init__(self, checker) -> None:
        self.checker = checker
        self.inttype = checker.named_type("builtins.int")
        self.booltype = checker.named_type("builtins.bool")
        self.strtype = checker.named_type("builtins.str")
       
    def get_header(self, vc):
        header = ''
        for v in vc.context + vc.lhs + vc.rhs:
            cas = carray_pred(v)
            for ca in cas:
                dump = self.smt_iarr(ca.args, vc.tmap)
                header += f'(assert (= (len {dump}) {len(ca.args)}))\n'
        return header
    def getsubclasses(self, C):
        # Only work for a single file
        r = []
        for nm in self.checker.globals:
            ent = self.checker.globals[nm]
            if isinstance(ent, TypeInfo):
                if C in ent.bases:
                    r.append(ent.name)
        return r
    def field_names(self, info):
        fs_orig = []
        for cc in reversed(info.bases):
            if cc.name == 'object':
                continue
            for n in cc.names:
                if isinstance(cc.names[n], Var):
                    fs_orig.append((n, cc.names[n].type))
        return fs_orig
    def expr_to_script(self, x: Expr, tmap): 
        if isinstance(x, InterpretedConstant):
            return str(x.constant), self.inttype
        
        if isinstance(x, SymConstant):
            return x.constant, self.strtype
        
        if isinstance(x, Variable):
            assert x.var in tmap
            return printVar(x, '_'), tmap[x.var]
        if isinstance(x, Attr):
            # return printAttr(x, '_')
            obj_str, obj_type = self.expr_to_script(x.obj, tmap)
            at = self.checker.getProp(obj_type.type, x.field)
            return "(" + obj_type.type.name + '__' + x.field + " " + " ".join((obj_str,)) + ")", at.base_type
        if isinstance(x, App):
            if x.func.startswith("cast"):
                pass
            elif x.func.startswith("isinstance"):
                pass
            else:
                assert x.func.endswith('__Ctor')
                if len(x.args) == 0:
                    return x.func, self.checker.named_type(x.func[:-6])
                else:
                    args = [self.expr_to_script(z, tmap) for z in x.args]
                    return "(" + x.func + " " + " ".join([x[0] for x in args]) + ")", self.checker.named_type(x.func[:-6])
        if isinstance(x, Let):
            e1_, t1_ = self.expr_to_script(x.e1, tmap)
            e2_, t2_ = self.expr_to_script(x.e2, cons(tmap, x.vname, t1_))
            return f"(let (({x.vname} {e1_})) {e2_})", t2_
        if isinstance(x, Bin):
            if x.op.op == "and":
                return "(" + x.op.op  + " " + self.expr_to_script(x.left, tmap)[0] + " " + self.expr_to_script(x.right, tmap)[0] + ")", self.booltype
            else:
                return "(" + x.op.op  + " " + self.expr_to_script(x.left, tmap)[0] + " " + self.expr_to_script(x.right, tmap)[0] + ")", self.inttype
        if isinstance(x, Call): 
            ece, tce = self.expr_to_script(x.callee, tmap)
            args = [self.expr_to_script(z, tmap) for z in x.args]
            at = self.checker.getProp(tce.type, x.method)
            return "(" + tce.type.name + '__' + x.method  + " " + ece + " " + " ".join([x[0] for x in args]) + ")", at.base_type.ret_type
        if isinstance(x, If): 
            econd, tcond = self.expr_to_script(x.cond, tmap)
            eif, tif = self.expr_to_script(x.if_expr, tmap)
            eelse, telse = self.expr_to_script(x.else_expr, tmap)
            return "(" + f"ite {econd} {eif} {eelse}" + ")", tif
        if isinstance(x, Uop):
            e, t = self.expr_to_script(x.operand, tmap)
            return "(" + f"not {e}" + ")", t
        assert False
    def expr_to_script_(self, x: Expr, tmap):
        return self.expr_to_script(x, tmap)[0]
    def get_names(self, vc) -> Set[tuple[str, Type]]:
        r = []  
        tmap = vc.tmap
        for v in vc.context + vc.lhs + vc.rhs:
            names = var_pred_dump(v)
            for name in names:
                if isinstance(name, Variable):
                    assert name.var in tmap
                    r.append((name.var, tmap[name.var]))
                else:
                    assert False
        return set(r)
    def conj(self, x:List[str]) -> str:
        if len(x) == 0:
            return "true"
        else:
            return f"(and {' '.join(x)} )"
    def disj(self, x:List[str]) -> str:
        if len(x) == 0:
            return "true"
        else:
            return f"(or {' '.join(x)} )"
    def translate_vc(self, vc, type_cons) -> str:
        p_ = self.conj(type_cons + [self.expr_to_script_(v, vc.tmap) for v in vc.context + vc.lhs])
        q_ = self.conj([self.expr_to_script_(v, vc.tmap) for v in vc.rhs])
        return f"(=>  {p_} {q_} )"
    def translate_head(self, vc) -> str:
        p_ = self.conj([self.expr_to_script_(v, vc.tmap) for v in vc.context + vc.lhs])
        return p_
    def translate_goal(self, vc) -> str:
        q_ = self.conj([self.expr_to_script_(v, vc.tmap) for v in vc.rhs])
        return q_
    
    def declare_var(self, name):
        return f"({name[0]} {self.translate_type(name[1])})"
    def declare_vars(self, names):
        return " ".join(self.declare_var(name) for name in names)
    def uquantify(self, names, vc_smt):
        return "(forall (" + self.declare_vars(names) + ")" + vc_smt + ")"
    def tc(self, name):
        # we must ensure all delacred tags correct (which means we should not use equality), otherwise unsoundess will occur (check tagProblem.smtlib)
        return f"(Subclass (Tag {name[0]}) {self.translate_type(name[1], keep_class=True)})"
    def not_prim(self, t):
        if str(t) == 'builtins.int' or str(t) == 'builtins.bool':
            return False
        return True
    def type_cons(self, names):
        return [self.tc(name) for name in names if self.not_prim(name[1])]
    
    def equantify(self, names, vc_smt):
        return "(exists (" + self.declare_vars(names) + ")" + vc_smt + ")"
    
    def translate_type(self, t:Type, keep_class=False):
        if str(t) == 'builtins.int':
            return "Int"
        elif str(t) == 'builtins.bool':
            return "Bool"
        else:
            if keep_class and isinstance(t, ObjectType):
                return t.type.name
            else:
                return "Object"
    def translate_type_info(self, t:TypeInfo):
        return t.name
    
    def get_field_string(self, cinfo):
        for n in cinfo.names:
            pass

    def generate_subc(self, argts, index=""):
        if any(self.not_prim(t) for n,t in argts):
            return '(and '  + ' '.join(f'(Subclass (Tag {n}{index}) {self.translate_type(t, True)})' for n,t in argts if self.not_prim(t)) + ' )'
        else:
            return 'true'
        
    def is_final(self, cd, name):
        subcs = self.getsubclasses(cd.info)
        for subc in subcs:
            cd2 = self.checker.named_type(subc).type.defn
            if cd2 != cd and name in [x.name for x in cd2.defs.body if isinstance(x, FuncDef)]:
                # overridden
                return False
        return True
    def transCT_final(self, class_defs:List[ClassDef]):
        r = ''
        interfaces = []
        # declare constructors and methods
        for cd in class_defs:
            assert cd.info
            is_interface =  len(cd.decorators) > 0
            if is_interface:
                interfaces.append(cd.name)
            r += f"(declare-const {cd.name} ClassName)\n"
            # subclass axiom
            r += f'(assert (Subclass {cd.name} {self.translate_type_info(cd.info.base)}))\n'
            if not is_interface:
                fields = []
                for cc in reversed(cd.info.bases):
                    if cc.name == 'object':
                        continue
                    for n in cc.names:
                        nd = cc.names[n]
                        if isinstance(nd, Var) and nd.type:
                            tt = nd.type
                            fields.append((n, self.translate_type(tt)))
                field_string = ' '.join(x[1] for x in fields)
                # transfer function declaration
                r += f'(declare-fun {cd.name}__Ctor ({field_string}) Object)\n'
            
            for name in cd.info.names:
                dd = cd.info.names[name]
                if not isinstance(dd, FuncDef) or dd.name == "__init__":
                    continue
                else:
                    xd = dd
                
                assert isinstance(xd.ref_type, FunctionType)
                ftmap = {n:t for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)}
                fname = cd.name + "__" + xd.name
                args = ' '.join([x for x in xd.arg_names if x])
                argts = [(n,t) for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)]
                argts_ = ' '.join(f'({n} {self.translate_type(t)})' for n,t in argts)
                argto = ' '.join(f'{self.translate_type(t)} ' for n,t in argts)
                r += f'(declare-fun {fname} ({argto}) {self.translate_type(xd.ref_type.ret_type)})\n'
        # here is a problem to remove fields 
        constructor_suite:List[tuple[List[tuple[str,Type]], str]] = []
        for cd in class_defs:
            
            # tag axioms
            assert cd.info
            subcs = self.getsubclasses(cd.info)
            case_cons = []
            for subc in subcs:
                if subc in interfaces:
                    # ignoring the interface
                    continue
                self_name = "self"
                fs_orig = self.field_names(self.checker.named_type(subc).type)
                field_string2 = ' '.join(f'({x[0]} {self.translate_type(x[1])})' for i, x in enumerate(fs_orig)) 
                field_string22 = ' '.join(f'{x[0]}' for i, x in enumerate(fs_orig)) 
                subcons = self.generate_subc(fs_orig)
                if len(fs_orig) == 0:
                    case_cons.append(f"(= {self_name} {subc}__Ctor)")
                else:
                    case_cons.append(f"(exists ({field_string2}) (and {subcons} (= {self_name} ({subc}__Ctor {field_string22}))))")
            r += f"(assert (forall ((self Object)) (=> (Subclass (Tag self) {cd.name}) {self.disj(case_cons)}) ))   ;Generatedness-Const-of-{cd.name}__Ctor\n"


            fs_orig = self.field_names(cd.info)
            field_string0 = ' '.join(f'({x[0]}{0} {self.translate_type(x[1])})' for x in fs_orig) 
            field_string00 = ' '.join(f'{x[0]}{0}' for x in fs_orig) 
            field_string1 = ' '.join(f'({x[0]}{1} {self.translate_type(x[1])})' for x in fs_orig) 
            field_string11 = ' '.join(f'{x[0]}{1}' for x in fs_orig)
            
            # field axiom
            
            subcon0 = self.generate_subc(fs_orig, index="0")
            subcon1 = self.generate_subc(fs_orig, index="1")
            
            if cd.name not in interfaces:
                constructor_suite.append((fs_orig, cd.name))
                # Constructor Tagging
                if len(fs_orig) > 0:
                    r += f'(assert (forall ({field_string0}) (=> {subcon0} (Subclass (Tag ({cd.name}__Ctor {field_string00})) {cd.name}))))   ;TagCtor-Const-of-{cd.name}__Ctor\n'
                    
                else:
                    r += f'(assert (=> {subcon0} (Subclass (Tag {cd.name}__Ctor {field_string00}) {cd.name})))   ;TagCtor-Const-of-{cd.name}__Ctor\n'
            
                for i, f in enumerate(fs_orig):
                    faf = cd.name + "__" + f[0]
                    r += f'(declare-fun {faf} (Object) {self.translate_type(f[1])})\n'
                    fs_orig[i][1].type.name
                    # field access tagging
                    if self.translate_type(f[1]) == "Object":
                        r += f'(assert (forall ((self Object)) (=> (Subclass (Tag self) {cd.name}) (Subclass (Tag ({faf} self)) {fs_orig[i][1].type.name}))))\n'
                    # injectivity
                    r += f'(assert (forall ({field_string0} {field_string1}) (=> {self.conj([subcon0, subcon1])} (=> (= ({cd.name}__Ctor {field_string00}) ({cd.name}__Ctor {field_string11})) (= {f[0]}0 {f[0]}1))  )))\n'
                    subcs = self.getsubclasses(cd.info)
                    for subc in subcs:
                        fs_orig = self.field_names(self.checker.named_type(subc).type)
                        field_string0_ = ' '.join(f'({x[0]}0 {self.translate_type(x[1])})' for i, x in enumerate(fs_orig)) 
                        field_string00_ = ' '.join(f'{x[0]}0' for i, x in enumerate(fs_orig)) 
                        subcon0 = self.generate_subc(fs_orig, index="0")
                        r += f'(assert (forall ({field_string0_}) (=> {subcon0} (= ({faf} ({self.checker.named_type(subc).type.name}__Ctor {field_string00_})) {f[0]}0))))   ;FA-Const-of-{cd.name}__Ctor\n'
                    
            # method axiom
            declared = set()
            for d in cd.defs.body:
                if isinstance(d, FuncDef):
                    xd = d
                    if isinstance(xd.body.body[0], PassStmt):
                        continue
                    ftmap = {n:t for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)}
                    fname = cd.name + "__" + xd.name
                    declared.add(fname)
                    args = ' '.join(n for n in xd.arg_names if n)
                    argts = [(n,t) for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)]
                    argts_ = ' '.join(f'({n} {self.translate_type(t)})' for n,t in argts)
                    argto = ' '.join(f'{self.translate_type(t)} ' for n,t in argts)
                    subcon = '(and '  + ' '.join(f'(Subclass (Tag {n}) {self.translate_type(t, True)})' for n,t in argts if self.not_prim(t)) + ' )'
                    if self.is_final(cd, d.name) and not xd.name == "__init__":
                        body = self.expr_to_script(transform_let(xd.body.body), ftmap)[0]
                        r += f'(assert (forall ({argts_}) (=> {subcon} (= ({fname} {args}) {body}))))\n'
                        if self.translate_type(xd.ref_type.ret_type) == "Object":
                            r += f'(assert (forall ({argts_}) (=> {subcon} (Subclass (Tag ({fname} {args})) {xd.ref_type.ret_type.type.name}))))\n'
                    # inhertance axiom
                    inherted = set()
                    for b in cd.info.bases:
                        if b == cd.info:
                            continue
                        pcd = b.defn
                        for xdd in pcd.defs.body:
                            if isinstance(xdd, (FuncDef)):
                                pass
                            else:
                                continue
                            if xdd.name == '__init__':
                                continue
                            if xdd.name != xd.name:
                                continue
                            fname = cd.name + "__" + xd.name
                            if fname not in inherted:
                                inherted.add(fname)
                                r += f'(assert (forall ({argts_}) (=> {subcon} (= ({fname} {args}) ({self.translate_type_info(b)}__{xd.name} {args})))))\n'
        # discrimiate
        for i, c1 in enumerate(constructor_suite):
            for j, c2 in enumerate(constructor_suite):
                if i != j:
                    fields_ = ' '.join(f'(v{i} {self.translate_type(x[1])})' for i, x in enumerate(c1[0]+c2[0])) 
                    fields_name1 = ' '.join(f'v{i}' for i, x in enumerate(c1[0]))
                    fields_name2 = ' '.join(f'v{i+len(c1[0])}' for i, x in enumerate(c2[0]))
                    if fields_name1 == "":
                        cc1 = f"{c1[1]}__Ctor"
                    else:
                        cc1 = f"({c1[1]}__Ctor {fields_name1})"
                    if fields_name2 == "":
                        cc2 = f"{c2[1]}__Ctor"
                    else:
                        cc2 = f"({c2[1]}__Ctor {fields_name2})"
                    if fields_ == "":
                        r += f'(assert (not (= {cc1} {cc2})))   ;Discrimiate-Const-of-{c1[1]}__{c2[1]}\n'
                    else:
                        r += f'(assert (forall ({fields_}) (not (= {cc1} {cc2}))))   ;Discrimiate-Const-of-{c1[1]}__{c2[1]}\n'
        a = 1
        return r
    def method_defn(self, m, C):
        r = self.checker.getProp_node(self.checker.named_type(C).type,m)
        assert r
        return r
    def transCT_conditional(self, class_defs:List[ClassDef]):
        r = ''
        interfaces = []
        # declare constructors and methods
        for cd in class_defs:
            assert cd.info
            is_interface =  len(cd.decorators) > 0
            if is_interface:
                interfaces.append(cd.name)
            r += f"(declare-const {cd.name} ClassName)\n"
            # subclass axiom
            r += f'(assert (Subclass {cd.name} {self.translate_type_info(cd.info.base)}))\n'
            if not is_interface:
                fields = []
                for cc in reversed(cd.info.bases):
                    if cc.name == 'object':
                        continue
                    for n in cc.names:
                        nd = cc.names[n]
                        if isinstance(nd, Var) and nd.type:
                            tt = nd.type
                            fields.append((n, self.translate_type(tt)))
                field_string = ' '.join(x[1] for x in fields)
                # transfer function declaration
                r += f'(declare-fun {cd.name}__Ctor ({field_string}) Object)\n'
            
            for name in cd.info.names:
                dd = cd.info.names[name]
                if not isinstance(dd, FuncDef) or dd.name == "__init__":
                    continue
                else:
                    xd = dd
                
                assert isinstance(xd.ref_type, FunctionType)
                ftmap = {n:t for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)}
                fname = cd.name + "__" + xd.name
                args = ' '.join([x for x in xd.arg_names if x])
                argts = [(n,t) for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)]
                argts_ = ' '.join(f'({n} {self.translate_type(t)})' for n,t in argts)
                argto = ' '.join(f'{self.translate_type(t)} ' for n,t in argts)
                r += f'(declare-fun {fname} ({argto}) {self.translate_type(xd.ref_type.ret_type)})\n'
            # implementation function declaration
            for d in cd.defs.body:
                if not isinstance(d, FuncDef) or d.name == "__init__":
                    continue
                else:
                    xd = d
                # if isinstance(xd.body.body[0], PassStmt):
                #     continue
                subcs = self.getsubclasses(cd.info)
                
                for subc in subcs:
                    if subc in interfaces:
                        # ignoring the interface
                        continue
                    cd2 = self.checker.named_type(subc).type.defn
                    if cd2 != cd and xd.name in [x.name for x in cd2.defs.body if isinstance(x, FuncDef)]:
                        # overridden
                        break
                    assert isinstance(xd.ref_type, FunctionType)
                    ftmap = {n:t for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)}
                    fname_imp = cd2.name + "__" + xd.name + "__IMP"
                    args = ' '.join([x for x in xd.arg_names if x])
                    argts = [(n,t) for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)]
                    argts_ = ' '.join(f'({n} {self.translate_type(t)})' for n,t in argts)
                    argto = ' '.join(f'{self.translate_type(t)} ' for n,t in argts)
                    
                    
                    r += f'(declare-fun {fname_imp} ({argto}) {self.translate_type(xd.ref_type.ret_type)})\n'
            fs_orig = self.field_names(cd.info)
            for i, f in enumerate(fs_orig):
                faf = cd.name + "__" + f[0]
                r += f'(declare-fun {faf} (Object) {self.translate_type(f[1])})\n'
        # here is a problem to remove fields 
        constructor_suite:List[tuple[List[tuple[str,Type]], str]] = []
        for cd in class_defs:
            
            # tag axioms
            assert cd.info
            subcs = self.getsubclasses(cd.info)
            case_cons = []
            for subc in subcs:
                if subc in interfaces:
                    # ignoring the interface
                    continue
                self_name = "self"
                fs_orig = self.field_names(self.checker.named_type(subc).type)
                field_string2 = ' '.join(f'({x[0]} {self.translate_type(x[1])})' for i, x in enumerate(fs_orig)) 
                field_string22 = ' '.join(f'{x[0]}' for i, x in enumerate(fs_orig)) 
                subcons = self.generate_subc(fs_orig)
                # TODO, no type for constructor arguments for now.
                if len(fs_orig) == 0:
                    case_cons.append(f"(= {self_name} {subc}__Ctor)")
                else:
                    case_cons.append(f"(exists ({field_string2}) (and {subcons} (= {self_name} ({subc}__Ctor {field_string22}))))")
            r += f"(assert (forall ((self Object)) (=> (Subclass (Tag self) {cd.name}) {self.disj(case_cons)}) ))   ;Generatedness-Const-of-{cd.name}__Ctor\n"


            fs_orig = self.field_names(cd.info)
            field_string0 = ' '.join(f'({x[0]}{0} {self.translate_type(x[1])})' for x in fs_orig) 
            field_string00 = ' '.join(f'{x[0]}{0}' for x in fs_orig) 
            field_string1 = ' '.join(f'({x[0]}{1} {self.translate_type(x[1])})' for x in fs_orig) 
            field_string11 = ' '.join(f'{x[0]}{1}' for x in fs_orig)
            
            # field axiom
            
            subcon0 = self.generate_subc(fs_orig, index="0")
            subcon1 = self.generate_subc(fs_orig, index="1")
            
            if cd.name not in interfaces:
                constructor_suite.append((fs_orig, cd.name))
                # Constructor Tagging
                if len(fs_orig) > 0:
                    r += f'(assert (forall ({field_string0}) (=> {subcon0} (Subclass (Tag ({cd.name}__Ctor {field_string00})) {cd.name}))))   ;TagCtor-Const-of-{cd.name}__Ctor\n'
                    
                else:
                    r += f'(assert (=> {subcon0} (Subclass (Tag {cd.name}__Ctor {field_string00}) {cd.name})))   ;TagCtor-Const-of-{cd.name}__Ctor\n'
            
                for i, f in enumerate(fs_orig):
                    faf = cd.name + "__" + f[0]
                    # r += f'(declare-fun {faf} (Object) {self.translate_type(f[1])})\n'
                    fs_orig[i][1].type.name
                    # field access tagging
                    if self.translate_type(f[1]) == "Object":
                        r += f'(assert (forall ((self Object)) (=> (Subclass (Tag self) {cd.name}) (Subclass (Tag ({faf} self)) {fs_orig[i][1].type.name}))))\n'
                    # injectivity
                    r += f'(assert (forall ({field_string0} {field_string1}) (=> {self.conj([subcon0, subcon1])} (=> (= ({cd.name}__Ctor {field_string00}) ({cd.name}__Ctor {field_string11})) (= {f[0]}0 {f[0]}1))  )))\n'
                    subcs = self.getsubclasses(cd.info)
                    for subc in subcs:
                        fs_orig = self.field_names(self.checker.named_type(subc).type)
                        field_string0_ = ' '.join(f'({x[0]}0 {self.translate_type(x[1])})' for i, x in enumerate(fs_orig)) 
                        field_string00_ = ' '.join(f'{x[0]}0' for i, x in enumerate(fs_orig)) 
                        subcon0 = self.generate_subc(fs_orig, index="0")
                        r += f'(assert (forall ({field_string0_}) (=> {subcon0} (= ({faf} ({self.checker.named_type(subc).type.name}__Ctor {field_string00_})) {f[0]}0))))   ;FA-Const-of-{cd.name}__Ctor\n'
                    
                    
                    
            # transfer function semantics: if final, then give semantics directly; else, casing on all possible classes
            for name in cd.info.names:
                dd = cd.info.names[name]
                if not isinstance(dd, FuncDef) or dd.name == "__init__":
                    continue
         
                xd = dd
                assert isinstance(xd.ref_type, FunctionType)
                ftmap = {n:t for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)}
                fname = cd.name + "__" + xd.name
                fname_imp = cd.name + "__" + xd.name + "__IMP"
                args = ' '.join([x for x in xd.arg_names if x])
                argts = [(n,t) for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)]
                argts_ = ' '.join(f'({n} {self.translate_type(t)})' for n,t in argts)
                argto = ' '.join(f'{self.translate_type(t)} ' for n,t in argts)
                subcon = '(and '  + ' '.join(f'(Subclass (Tag {n}) {self.translate_type(t, True)})' for n,t in argts if self.not_prim(t)) + ' )'
                if self.is_final(cd, xd.name) and not xd.name == "__init__" and not isinstance(xd.body.body[0], PassStmt):
                    body = self.expr_to_script(transform_let(xd.body.body), ftmap)[0]
                    r += f'(assert (forall ({argts_}) (=> {subcon} (= ({fname} {args}) {body}))))   ;Transfer-Const-of-{fname}\n'
                    if self.translate_type(xd.ref_type.ret_type) == "Object":
                        r += f'(assert (forall ({argts_}) (=> {subcon} (Subclass (Tag ({fname} {args})) {xd.ref_type.ret_type.type.name}))))\n'
                    # inhertance axiom
                    inherted = set()
                    for b in cd.info.bases:
                        if b == cd.info:
                            continue
                        pcd = b.defn
                        for xdd in pcd.defs.body:
                            if isinstance(xdd, (FuncDef)):
                                pass
                            else:
                                continue
                            if xdd.name == '__init__':
                                continue
                            if xdd.name != xd.name:
                                continue
                            fname = cd.name + "__" + xd.name
                            if fname not in inherted:
                                inherted.add(fname)
                                r += f'(assert (forall ({argts_}) (=> {subcon} (= ({fname} {args}) ({self.translate_type_info(b)}__{xd.name} {args})))))   ;Inherit-Const-of-{fname}\n'
                else:
                    subcon0 = self.generate_subc(argts)
                    subcs = self.getsubclasses(cd.info)
                    case_cons = []
                    for subc in subcs:
                        if subc in interfaces:
                            # ignoring the interface
                            continue
                        if xd.arg_names[0]:
                            self_name = xd.arg_names[0]
                            fs_orig = self.field_names(self.checker.named_type(subc).type)
                            field_string2 = ' '.join(f'({x[0]}0 {self.translate_type(x[1])})' for i, x in enumerate(fs_orig)) 
                            field_string22 = ' '.join(f'{x[0]}0' for i, x in enumerate(fs_orig)) 
                            fname_imp_ = subc + "__" + xd.name + "__IMP"
                            subcon = self.generate_subc(fs_orig, index="0")
                            xdd = self.method_defn(xd.name, subc)
                            assert isinstance(xdd, FuncDef)
                            if isinstance(xdd.body.body[0], PassStmt):
                                continue
                            ftmap = {n:t for n,t in zip(xdd.ref_type.arg_names, xdd.ref_type.arg_types)}
                            body = self.expr_to_script(transform_let(xdd.body.body), ftmap)[0]
                            if len(fs_orig) == 0:
                                case_cons.append(f"(forall ({argts_+field_string2}) (=> (and {subcon} (= {self_name} {subc}__Ctor)) (= ({fname} {args}) {body})))")
                            else:
                                case_cons.append(f"(forall ({argts_+field_string2}) (=> (and {subcon} (= {self_name} ({subc}__Ctor {field_string22}))) (= ({fname} {args}) {body})))")
                    r += f'(assert {self.conj(case_cons)})   ;Transfer-Const-of-{fname}\n'
                    # transfer function tagging
                    if isinstance(xd.ref_type.ret_type, ObjectType) and self.translate_type(xd.ref_type.ret_type) == "Object" :
                        r += f'(assert (forall ({argts_}) (=> {subcon0} (Subclass (Tag ({fname} {args})) {xd.ref_type.ret_type.type.name}))))   ;TransferRet-Const-of-{fname_imp}\n'
                
            # implementation function semantics
            for d in cd.defs.body:
                if not isinstance(d, FuncDef) or d.name == "__init__":
                    continue
    
                xd = d
                subcs = self.getsubclasses(cd.info)
                for subc in subcs:
                    if subc in interfaces:
                        # ignoring the interface
                        continue

                    cd2 = self.checker.named_type(subc).type.defn
                    if cd2 != cd and xd.name in [x.name for x in cd2.defs.body if isinstance(x, FuncDef)]:
                        # overridden
                        break
                    assert isinstance(xd.ref_type, FunctionType)
                    
                    ftmap = {n:t for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)}
                    fname_imp = subc + "__" + xd.name + "__IMP"
                    args = ' '.join([x for x in xd.arg_names if x])
                    argts = [(n,t) for n,t in zip(xd.ref_type.arg_names, xd.ref_type.arg_types)]
                    argts_ = ' '.join(f'({n} {self.translate_type(t)})' for n,t in argts)
                    argto = ' '.join(f'{self.translate_type(t)} ' for n,t in argts)
                    
                    subcon = self.generate_subc(argts)
                    
                    
                    if not isinstance(xd.body.body[0], PassStmt) and not xd.name == "__init__":
                        # exclude interface methods
                        body = self.expr_to_script(transform_let(xd.body.body), ftmap)[0]
                        r += f'(assert (forall ({argts_}) (=> {subcon} (= ({fname_imp} {args}) {body}))))   ;Implementation-Const-of-{fname_imp}\n'
                        if isinstance(xd.ref_type.ret_type, ObjectType) and self.translate_type(xd.ref_type.ret_type) == "Object" :
                            # implementation function tagging
                            r += f'(assert (forall ({argts_}) (=> {subcon} (Subclass (Tag ({fname_imp} {args})) {xd.ref_type.ret_type.type.name}))))   ;ImplementationRet-Const-of-{fname_imp}\n'
                
            
        # discrimiate
        for i, c1 in enumerate(constructor_suite):
            for j, c2 in enumerate(constructor_suite):
                if i != j:
                    fields_ = ' '.join(f'(v{i} {self.translate_type(x[1])})' for i, x in enumerate(c1[0]+c2[0])) 
                    fields_name1 = ' '.join(f'v{i}' for i, x in enumerate(c1[0]))
                    fields_name2 = ' '.join(f'v{i+len(c1[0])}' for i, x in enumerate(c2[0]))
                    if fields_name1 == "":
                        cc1 = f"{c1[1]}__Ctor"
                    else:
                        cc1 = f"({c1[1]}__Ctor {fields_name1})"
                    if fields_name2 == "":
                        cc2 = f"{c2[1]}__Ctor"
                    else:
                        cc2 = f"({c2[1]}__Ctor {fields_name2})"
                    if fields_ == "":
                        r += f'(assert (not (= {cc1} {cc2})))   ;Discrimiate-Const-of-{c1[1]}__{c2[1]}\n'
                    else:
                        r += f'(assert (forall ({fields_}) (not (= {cc1} {cc2}))))   ;Discrimiate-Const-of-{c1[1]}__{c2[1]}\n'
        a = 1
        return r
    def convert_vc_smtlib(self, vc: VC, class_defs:List[ClassDef]):
        with open('.smt/head_cls.smtlib', 'r+') as f:
            head = f.read()
        CT_axioms = self.transCT_conditional(class_defs)
        header = self.get_header(vc)
        names = self.get_names(vc)
        type_cons = self.type_cons(names)
        vc_smt = self.translate_vc(vc, type_cons)

        body = self.uquantify(names, vc_smt)
        body2 = "true"
        return head + CT_axioms + header + f"(assert (not {self.conj([body, body2])} ))\n(check-sat)"
    def write(self, vcs:List[VC], class_defs:List[ClassDef], filename=None):
        for i, vc in enumerate(vcs):
            content = self.convert_vc_smtlib(vc, class_defs)
            print("Line: " + str(vc.line))
            print("Subtype: " + printExpr(vc.lhs[0]))
            print("Supertype: " + printExpr(vc.rhs[0]))
            # if not (vc.line == 130 ):#and printExpr(vc.rhs[0]) == "(if ((self. get(y)) = OkType__Ctor([s])) then ((Cons__Ctor([x;t;self]). get(y)) = OkType__Ctor([s])) else true )"):
            #     continue
            if filename == None:
                with open('.smt/default.smtlib', 'w+') as f:
                    f.write(content)
            cwd = os.getcwd()
            # We use both Z3 4.12 and 4.8 since their search strategies can be complement
            try:
                ret = subprocess.run(f"{cwd}/lib/z3 {cwd}/.smt/default.smtlib", shell=True, capture_output=True, text=True, executable="/bin/bash", timeout=10)
                print('Checking finishs with returncode:', ret.stdout)
                if ret.stdout == 'unsat\n':
                    pass
                elif ret.stdout == 'sat\n':
                    print('Checking returns sat, examine this subtyping again!!!.')
                    self.checker.errors.report(vc.line, None, message = "SMT Checking Failed")
            except subprocess.TimeoutExpired as ex:
                try:
                    ret = subprocess.run(f"z3 {cwd}/.smt/default.smtlib", shell=True, capture_output=True, text=True, executable="/bin/bash", timeout=30)
                    print('Checking finishs with returncode:', ret.stdout)
                    if ret.stdout == 'unsat\n':
                        pass
                    elif ret.stdout == 'sat\n':
                        print('Checking returns sat, examine this subtyping again!!!.')
                        self.checker.errors.report(vc.line, None, message = "SMT Checking Failed")
                except subprocess.TimeoutExpired as ex:
                    print('Checking runs timeout, examine this subtyping again!!!.')
                    self.checker.errors.report(vc.line, None, message = "SMT Checking Failed")
            