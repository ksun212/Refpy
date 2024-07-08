

from __future__ import annotations

import argparse
import sys
from refpy import driver
from refpy.source_utils import create_source_list, BuildSource
from refpy.options import Options

def process_options(args: list[str],) -> tuple[list[BuildSource], Options]:
    

    parser = argparse.ArgumentParser(
        fromfile_prefix_chars="@",
        add_help=False,
    )
    
    code_group = parser.add_argument_group(
        title="Running code",
        description="Code to type check",
    )
    code_group.add_argument(
        metavar="files",
        nargs="*",
        dest="files",
        help="Type-check given files or directories",
    )
    opt = parser.parse_args(args, argparse.Namespace())
    options = Options()
    targets = create_source_list(opt.files, options)
    return targets, options

def main() -> None:
    
    args = sys.argv[1:]
    sources, options = process_options(args)

    res = driver.build(sources, options)
    n_errors = len(res)
    if n_errors:
        print(f"{len(res)} Error(s) Detected!")
        for e in res:
            print(e)
    elif not res:
        print("Success!")


main()