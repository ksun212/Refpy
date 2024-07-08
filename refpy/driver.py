


from __future__ import annotations
import os
import time
from typing import (
    AbstractSet,
    Dict,
    Iterable,
    List,
    TypeVar,
)
from refpy.parse_and_convert import source_to_tree
from refpy.refchecker import RefChecker

from refpy.errors import ErrorCollectors
from refpy.nodes import Import, ImportAll, ImportFrom, RefpyFile
from refpy.semanal import SymboBinder
from refpy.semanal_pass1 import (
    SymbolBuilder
)
from refpy.source_utils import BuildSource, exists
from refpy.options import Options
from refpy.errors import ErrorCollectors
from refpy.nodes import RefpyFile
from refpy.options import Options

Graph = Dict[str, "Module"]



class Manager:

    def __init__(
        self,
        options: Options,
        errors: ErrorCollectors,
        sources: List[BuildSource]
    ) -> None:
        self.errors = errors
        self.options = options
        self.modules: dict[str, RefpyFile] = {}
        self.sources = sources
    def all_imported_modules_in_file(self, file: RefpyFile) -> list[tuple[str, int]]:

        def correct_rel_imp(imp: ImportFrom | ImportAll) -> str:
            
            file_id = file.fullname
            rel = imp.relative
            if rel == 0:
                return imp.id
            if os.path.basename(file.path).startswith("__init__."):
                rel -= 1
            if rel != 0:
                file_id = ".".join(file_id.split(".")[:-rel])
            new_id = file_id + "." + imp.id if imp.id else file_id

            return new_id

        res: list[tuple[str, int]] = []
        for imp in file.imports:
            if isinstance(imp, Import):
                for id, _ in imp.ids:
                    res.append((id, imp.line))
            elif isinstance(imp, ImportFrom):
                cur_id = correct_rel_imp(imp)
                res.append((cur_id, imp.line))

        res.sort(key=lambda x: -x[0].count("."))
        return res
    def parse_file(self, id: str, path: str, source: str, options: Options) -> RefpyFile:
        tree = source_to_tree(source, path, id, self.errors, options=options)
        tree._fullname = id
        return tree

    def find_module(self, id: str) -> str|None:
        components = id.split(".")
        python_path: list[str] = []
        for source in self.sources:
            
            if source.base_dir:
                dir = source.base_dir
                if dir not in python_path:
                    python_path.append(dir)
        candidate_base_dirs = python_path
        candidate_base_dirs += [os.getcwd() + "/refpy/typeshed/stdlib"]
        seplast = os.sep + components[-1]  
        sepinit = os.sep + "__init__"
        PYTHON_EXTENSIONS = [".py", ".pyi"]
        for base_dir in candidate_base_dirs:
            base_path = base_dir + seplast  
            dir_prefix = base_dir
            for _ in range(len(components) - 1):
                dir_prefix = os.path.dirname(dir_prefix)
            
            for extension in PYTHON_EXTENSIONS:
                path = base_path + sepinit + extension
                if exists(path):
                    return path
            
            for extension in PYTHON_EXTENSIONS:
                path = base_path + extension
                if exists(path):
                    return path
        return None

class ModuleNotFound(Exception):
    pass


class Module:

    manager: Manager
    id: str  
    path: str
    abspath: str | None = None  
    source: str | None = None  
    tree: RefpyFile | None = None
    dependencies: list[str]  
    ancestors: list[str] | None = None
    options: Options

    _ref_checker: RefChecker | None = None


    def __init__(
        self,
        id: str | None,
        path: str | None,
        manager: Manager,
    ) -> None:
        
        self.manager = manager
        self.id = id or "__main__"
        self.options = manager.options
        self._type_checker = None
        self._ref_checker = None
        
        if not path:
            assert id is not None
            try:
                path = manager.find_module(id)
            except ModuleNotFound:
                raise
        assert path
        self.path = path
        if path:
            self.abspath = os.path.abspath(path)
        self.add_ancestors()
        self.parse_file()
        self.compute_dependencies()


    def add_ancestors(self) -> None:
        if self.path is not None:
            _, name = os.path.split(self.path)
            base, _ = os.path.splitext(name)
            if "." in base:
                
                self.ancestors = []
                return
        
        ancestors = []
        parent = self.id
        while "." in parent:
            parent, _ = parent.rsplit(".", 1)
            ancestors.append(parent)
        self.ancestors = ancestors


    def parse_file(self) -> None:
        manager = self.manager

        modules = manager.modules

        with open(self.path, "rb") as f:
            source = f.read().decode()

        self.tree = manager.parse_file(self.id, self.path, source, self.options)
        modules[self.id] = self.tree
        self.tree.names = dict()

    def add_dependency(self, dep: str) -> None:
        if dep not in self.dependencies:
            self.dependencies.append(dep)

    def compute_dependencies(self) -> None:
        
        manager = self.manager
        assert self.tree is not None

        self.dependencies = []
        dep_entries = manager.all_imported_modules_in_file(
            self.tree
        )
        for id, line in dep_entries:
            if id == self.id:
                continue
            self.add_dependency(id)
        
        if self.id != "builtins":
            self.add_dependency("builtins")
    def ref_check_first_pass(self) -> None:
        self.ref_checker().check_first_pass()

    def ref_checker(self) -> RefChecker:
        if not self._ref_checker:
            assert self.tree is not None, "Internal error: must be called on parsed file only"
            manager = self.manager
            self._ref_checker = RefChecker(manager.modules, self.options, self.tree, self.path, manager.errors)
        return self._ref_checker
    

def build(sources: list[BuildSource], options: Options) -> list[str]:
    errors = ErrorCollectors(options, read_source=None)
    manager = Manager(options=options, errors=errors, sources = sources)
    graph = load_graph(sources, manager)
    error_list = process_graph(graph, manager)
    return error_list


def load_graph(sources: list[BuildSource], manager: Manager,) -> Graph:

    graph: Graph = {}
    new = []
    for bs in sources:
        try:
            st = Module(id=bs.module, path=bs.path, manager=manager)
        except ModuleNotFound:
            continue
        if st.id in graph:
            manager.errors.set_file(st.path, st.id, manager.options)
            manager.errors.report(-1,-1, f'Duplicate module named "{st.id}" (also at "{graph[st.id].path}")')
            assert False
        graph[st.id] = st
        new.append(st)

    seen_files = {st.abspath: st for st in graph.values() if st.path}

    for st in new:
        assert st.ancestors is not None
        dependencies = [dep for dep in st.dependencies]
        for dep in st.ancestors + dependencies:
            if dep not in graph:
                try:
                    if dep in st.ancestors:
                        newst = Module(id=dep, path=None, manager=manager)
                    else:
                        newst = Module(id=dep,path=None, manager=manager)
                except ModuleNotFound:
                    assert False
                else:
                    if newst.path:
                        newst_path = os.path.abspath(newst.path)
                        if newst_path in seen_files:
                            manager.errors.report( -1,0, "Source file found twice under different module names: " '"{}" and "{}"'.format(seen_files[newst_path].id, newst.id))
                            assert False

                        seen_files[newst_path] = newst

                    assert newst.id not in graph, newst.id
                    graph[newst.id] = newst
                    new.append(newst)
    return graph


def process_graph(graph: Graph, manager: Manager) -> list[str]:
    errors = []
    modules = sorted_modules(graph)
    for module in modules:
        errors.extend(process_module(graph, module, manager))
    return errors

def process_module(graph: Graph, mod: str, manager: Manager) -> list[str]:
    graph[mod].parse_file()
    semantic_analysis(graph, mod, manager)
    t = time.time()
    if 'ref_tests' in graph[mod].path:
        graph[mod].ref_check_first_pass()
    print("Time cost: " + str(time.time() - t) + " seconds")
    return manager.errors.file_messages(graph[mod].path)
T = TypeVar("T")
def topsort(data: dict[T, set[T]]) -> Iterable[set[T]]:
    for k, v in data.items():
        v.discard(k)  
    for item in set.union(*data.values()) - set(data.keys()):
        data[item] = set()
    while True:
        ready = {item for item, dep in data.items() if not dep}
        if not ready:
            break
        yield ready
        data = {item: (dep - ready) for item, dep in data.items() if item not in ready}
    assert not data, f"A cyclic dependency exists amongst {data!r}"
def sorted_modules(graph: Graph, vertices: AbstractSet[str] | None = None) -> list[str]:
    
    
    if vertices is None:
        vertices = set(graph)
    edges = {id: set(graph[id].dependencies) for id in vertices}
    
    res:list[str] = []
    for ready in topsort(edges):
        res.extend(ready)
    return res

def semantic_analysis(graph: Graph, mod: str, manager: Manager) -> None:
    
    state = graph[mod]
    tree = state.tree
    assert tree is not None
    binder = SymboBinder(manager.modules, manager.errors, manager.options)
    builder = SymbolBuilder(binder.modules)
    binder.global_table = tree.names
    tree.names["__builtins__"] = binder.modules["builtins"]
    builder.global_table = tree.names
    refresh_node = tree
    
    builder.begin(refresh_node, options=state.options)
    
    binder.begin(refresh_node)