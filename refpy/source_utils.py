"python source finder inspired by mypy"

from __future__ import annotations

import functools
import os
from typing import Sequence
from typing_extensions import Final
import stat
from refpy.options import Options

PY_EXTENSIONS: Final = (".pyi", ".py", )

class BuildSource:
    

    def __init__(
        self,
        path: str | None,
        module: str | None,
        text: str | None = None,
        base_dir: str | None = None,
        followed: bool = False,
    ) -> None:
        self.path = path  
        self.module = module or "__main__"  
        self.text = text  
        self.base_dir = base_dir  
        self.followed = followed  

    def __repr__(self) -> str:
        return (
            "BuildSource(path={!r}, module={!r}, has_text={}, base_dir={!r}, followed={})".format(
                self.path, self.module, self.text is not None, self.base_dir, self.followed
            )
        )

class InvalidSourceList(Exception):
    pass
def isdir(path: str) -> bool:
    try:
        st = os.stat(path)
    except OSError:
        return False
    return stat.S_ISDIR(st.st_mode)
def exists(path):
    try:
        os.stat(path)
    except OSError as err:
        return False
    return True
def create_source_list(
    paths: Sequence[str],
    options: Options,
) -> list[BuildSource]:
    
    finder = SourceFinder(options)

    sources = []
    for path in paths:
        path = os.path.normpath(path)
        if path.endswith(PY_EXTENSIONS):
            
            name, base_dir = finder.crawl_up(path)
            sources.append(BuildSource(path, name, None, base_dir))
        elif isdir(path):
            sub_sources = finder.find_sources_in_dir(path)
            sources.extend(sub_sources)
    return sources


def keyfunc(name: str) -> tuple[bool, int, str]:
    
    base, suffix = os.path.splitext(name)
    for i, ext in enumerate(PY_EXTENSIONS):
        if suffix == ext:
            return (base != "__init__", i, base)
    return (base != "__init__", -1, name)


def normalise_package_base(root: str) -> str:
    if not root:
        root = os.curdir
    root = os.path.abspath(root)
    if root.endswith(os.sep):
        root = root[:-1]
    return root



class SourceFinder:
    def __init__(self, options: Options) -> None:
        self.options = options

    def find_sources_in_dir(self, path: str) -> list[BuildSource]:
        sources = []

        seen: set[str] = set()
        names = sorted(os.listdir(path), key=keyfunc)
        for name in names:
            
            if name in ("__pycache__", "site-packages", "node_modules") or name.startswith("."):
                continue
            subpath = os.path.join(path, name)

            if isdir(subpath):
                sub_sources = self.find_sources_in_dir(subpath)
                if sub_sources:
                    seen.add(name)
                    sources.extend(sub_sources)
            else:
                stem, suffix = os.path.splitext(name)
                if stem not in seen and suffix in PY_EXTENSIONS:
                    seen.add(stem)
                    module, base_dir = self.crawl_up(subpath)
                    sources.append(BuildSource(subpath, module, None, base_dir))

        return sources

    def crawl_up(self, path: str) -> tuple[str, str]:
        path = os.path.abspath(path)
        parent, filename = os.path.split(path)

        module_name = strip_py(filename) or filename

        parent_module, base_dir = self.crawl_up_dir(parent)
        if module_name == "__init__":
            return parent_module, base_dir

        
        
        module = module_join(parent_module, module_name)
        return module, base_dir

    def crawl_up_dir(self, dir: str) -> tuple[str, str]:
        return self._crawl_up_helper(dir) or ("", dir)

    @functools.lru_cache()  
    def _crawl_up_helper(self, dir: str) -> tuple[str, str] | None:

        parent, name = os.path.split(dir)
        if name.endswith("-stubs"):
            name = name[:-6]  

        
        init_file = self.get_init_file(dir)
        if init_file is not None:
            if not name.isidentifier():
                
                
                raise InvalidSourceList(f"{name} is not a valid Python package name")
            
            mod_prefix, base_dir = self.crawl_up_dir(parent)
            return module_join(mod_prefix, name), base_dir

        
        if not name or not parent or not name.isidentifier():
            return None

        
        
        result = self._crawl_up_helper(parent)
        if result is None:
            
            
            return None
        
        
        mod_prefix, base_dir = result
        return module_join(mod_prefix, name), base_dir

    def get_init_file(self, dir: str) -> str | None:
        for ext in PY_EXTENSIONS:
            f = os.path.join(dir, "__init__" + ext)
            if exists(f):
                return f
        return None


def module_join(parent: str, child: str) -> str:
    
    if parent:
        return parent + "." + child
    return child


def strip_py(arg: str) -> str | None:
    
    for ext in PY_EXTENSIONS:
        if arg.endswith(ext):
            return arg[: -len(ext)]
    return None
