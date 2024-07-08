## Refinement Types for Python

This is the implementation of Refinement Featherweight Java (RFJ) for Python, named refpy. 
The basic infrastructure (parser, module&package handler) are inspired by and reuse the code of an open-source type checker of Python, mypy. 
Currently, some parts processed by the basic infrastrcuture (e.g., while loops, tuples, lists, and union types) are not utilized in the refinement type analysis. However, we want to support those in the future, and choose to keep them unused for now. 

### Structure
The module&package mechanism of refpy follows closely Python, and we reuse some codes of Mypy on handling the module&package mechanisms. 
build, modulefinder, fschache, findsources.

The semantic analysis. 
Refpy is built upon a simplified mypy (non-core functionalities, such as servers, tests are removed), it replace the mypy type checker with a refinement type checker. The refinement type checker is composed of four components:

refpy

------ refinements.py: basic definitions

------ refcheker.py: the type checker

------ ref_solver.py: an auxiliary solver (mostly legacy)

------ smt.py: the smt interface

Currently, the development is at a **very** primitive stage, some non-critical checkings (e.g., valid override) are not implemented. 

### Dependency
* Several Python Packages (typing_extensions, mypy_extensions, typed_ast, tomli)
* A Z3 Binary (Tested on 4.12)

### Tests
The ref_tests folder contains a basic test suite of refpy. In particular, ref_tests/pizza.py is the running example in the paper (note that we use passed class as interfaces, since PEP 484 does not provide interface types.).  

Basic usage: 
```
python -m refpy.main ref_tests/pizza.py
```

Note that the checker would terminate quickly if there is no type error. If there are type errors, the checker may not terminate, essentially due to Z3 does not terminate. In such cases, you should debug the subtyping constraint causing the stuck. 


### Instruction
1. Constructor functions can be left empty, their semantics are not used (see transCT), but their signatures (arity and type annotation) must be accurate, since the signatures would be used for type checking constructors. 