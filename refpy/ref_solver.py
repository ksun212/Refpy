from collections import defaultdict
from refpy.types import ObjectType, Type
from refpy.refinements import subExpr, Variable, vv, Expr
from typing import List, Dict
from dataclasses import dataclass
import itertools

@dataclass
class VC:
    tmap: Dict[str, Type]
    context: List[Expr]
    lhs: List[Expr]
    rhs: List[Expr]
    line: int
    
class RefSolver:
    def __init__(self):
        pass

    def make_bindings(self, bindings, seen_vars) -> List[tuple[str, List[Expr]]]:
        bs = [bindings[x] for x in bindings if x in seen_vars]
        old_bindings = []
        for name, b in bs:
            old_bindings.append((name, [subExpr({Variable(b.refinement.self_var): Variable(name)}, p) for p in b.refinement.pred]))
        return old_bindings

    def sym_exe(self, infosys):
        worklist = []
        for c in infosys.subs:
            seen_vars = c._senv 
            new_bindings = self.make_bindings(infosys.bs, seen_vars)
            new_context = list(itertools.chain.from_iterable([x[1] for x in new_bindings]))
            new_lhs = c.slhs.refinement.pred
            new_rhs = c.srhs.refinement.pred

            bs = [infosys.bs[x] for x in infosys.bs if x in seen_vars]
            tmap = {}
            for name, sr in bs:
                tmap[name] = sr.base_type
            tmap[vv()] = c.slhs.base_type
            worklist.append(VC(tmap, new_context, new_lhs, new_rhs, c.line))
        return worklist
    def check(self, infosys):
        worklist = self.sym_exe(infosys)
        
        return worklist