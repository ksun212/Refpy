from __future__ import annotations

from refpy.nodes import (
    AssignmentStmt,
    Block,
    ClassDef,
    FuncDef,
    FuncDef,
    FuncDef,
    Import,
    ImportAll,
    ImportFrom,
    RefpyFile,
    NameExpr,
    Node,
    SymbolNode,
    SymbolTable,
    TypeInfo,
    Var,
)
from refpy.options import Options
from refpy.visitor import NodeVisitor



class SymbolBuilder(NodeVisitor[None]):
    modules: dict[str, RefpyFile]
    global_table: SymbolTable
    current_class: TypeInfo | None = None
    options: Options
    cur_mod_id = ""

    def __init__(self, modules: dict[str, RefpyFile]) -> None:
        
        self.current_class = None
        self.modules = modules


    def begin(self, node:  RefpyFile, options: Options) -> None:
        self.cur_mod_id = node.fullname
        for d in node.defs:
            self.accept(d)

    def visit_func_def(self, defn: FuncDef) -> None:
        if self.is_class_scope():
            assert self.current_class is not None
            defn.info = self.current_class
        defn._fullname = self.qualified_name(defn.name)
        self.add_symbol(defn.name, defn)

    def visit_class_def(self, defn: ClassDef) -> None:
        defn.fullname = self.qualified_name(defn.name)
        info = self.mk_type_info(defn)
        if not defn.info:
            defn.info = info
            info.defn = defn
            info._fullname = defn.fullname
        self.add_symbol(defn.name, defn.info)
        self.current_class = info
        defn.defs.accept(self)
        self.current_class = None

    def mk_type_info(self, defn: ClassDef) -> TypeInfo:
        info = TypeInfo(dict(), defn, self.cur_mod_id)
        info.set_line(defn)
        return info

    def visit_import(self, i: Import) -> None:
        for id, as_id in i.ids:
            if as_id is not None:
                base_id = id
                imported_id = as_id
            else:
                base_id = id.split(".")[0]
                imported_id = base_id

            if base_id in self.modules:
                node = self.modules[base_id]
                self.add_symbol(imported_id, node)

    def visit_import_from(self, imp: ImportFrom) -> None:
        module_id = imp.id
        module = self.modules.get(module_id)
        for id, as_id in imp.names:
            fullname = module_id + "." + id
            node:SymbolNode|None = None
            if module is None:
                node = None
            elif module_id == self.cur_mod_id and fullname in self.modules:
                node = self.modules[fullname]
            else:
                node = module.names.get(id)
            imported_id = as_id or id

            if not node:
                mod = self.modules.get(fullname)
                if mod is not None:
                    node = mod
            if node:
                self.add_symbol(imported_id, node)

    def visit_import_all(self, i: ImportAll) -> None:
        i_id = i.id
        if i_id in self.modules:
            m = self.modules[i_id]
            for name, node in m.names.items():
                if node is None:
                    continue
                self.add_symbol(name, node)
                


    def visit_assignment_stmt(self, s: AssignmentStmt) -> None:
        assert isinstance(s.lvalues[0], NameExpr)
        lvalue = s.lvalues[0]
        if lvalue.node:
            return

        name = lvalue.name
        names = self.current_symbol_table()
        existing = names.get(name)

        if not existing:
            var = self.mk_var(lvalue)
            self.add_symbol(name, var)
            lvalue.node = var
            lvalue.fullname = lvalue.name
    def mk_var(self, node: NameExpr) -> Var:
        
        name = node.name
        v = Var(name)
        v.set_line(node)
        if self.current_class is not None:
            v.info = self.current_class
        v._fullname = self.qualified_name(name)
        return v

    def visit_block(self, b: Block) -> None:
        for s in b.body:
            self.accept(s)


    def add_symbol(self,name: str, node: SymbolNode) -> None:
        names = self.current_symbol_table()
        existing = names.get(name)
        assert not existing
        names[name] = node
        return None


    def qualified_name(self, name: str) -> str:
        if self.current_class is not None:
            return self.current_class._fullname + "." + name
        else:
            return self.cur_mod_id + "." + name

    def is_class_scope(self) -> bool:
        return self.current_class is not None

    def is_module_scope(self) -> bool:
        return self.current_class is None

    def current_symbol_table(self) -> SymbolTable:
        if self.current_class is not None:
            
            names = self.current_class.names
        else:
            
            names = self.global_table
        return names

    def accept(self, node: Node) -> None:
        node.accept(self)

