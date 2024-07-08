from __future__ import annotations

from typing import Callable, Iterable
from refpy.options import Options

class ErrorInfo:
    file = ""
    module: str | None = None
    line = 0  
    column = 0  
    end_line = 0  
    end_column = 0  
    message = ""

    def __init__(
        self,
        *,
        file: str,
        module: str | None,
        line: int,
        column: int,
        end_line: int,
        end_column: int,
        message: str,
    ) -> None:
        self.file = file
        self.module = module
        self.line = line
        self.column = column
        self.end_line = end_line
        self.end_column = end_column
        self.message = message


class ErrorCollectors:
    error_info_map: dict[str, list[ErrorInfo]]
    flushed_files: set[str]
    file: str = ""

    ignored_lines: dict[str, dict[int, list[str]]]
    ignored_files: set[str]

    target_module: str | None = None

    def __init__(
        self,
        options: Options,
        *,
        read_source: Callable[[str], list[str] | None] | None = None,
    ) -> None:
        self.options = options
        self.read_source = read_source
        self.initialize()

    def initialize(self) -> None:
        self.error_info_map = {}
        self.flushed_files = set()
        self.function_or_member = [None]
        self.ignored_lines = {}
        self.ignored_files = set()
        self.target_module = None

    def reset(self) -> None:
        self.initialize()

    def set_file(self, file: str, module: str | None, options: Options) -> None:
        self.file = file
        self.target_module = module
        self.options = options

    def current_target(self) -> str | None:
        
        return self.target_module

    def current_module(self) -> str | None:
        return self.target_module

    def report(
        self,
        line: int,
        column: int | None,
        message: str,
        *,
        file: str | None = None,
        origin_span: Iterable[int] | None = None,
        offset: int = 0,
        end_line: int | None = None,
        end_column: int | None = None,
    ) -> None:
    

        if column is None:
            column = -1
        if end_column is None:
            if column == -1:
                end_column = -1
            else:
                end_column = column + 1

        if file is None:
            file = self.file
        if offset:
            message = " " * offset + message

        if origin_span is None:
            origin_span = [line]

        if end_line is None:
            end_line = line

        info = ErrorInfo(
            file=file,
            module=self.current_module(),
            line=line,
            column=column,
            end_line=end_line,
            end_column=end_column,
            message=message,
        )
        self.add_error_info(info)

    def _add_error_info(self, file: str, info: ErrorInfo) -> None:
        assert file not in self.flushed_files
        if file not in self.error_info_map:
            self.error_info_map[file] = []
        self.error_info_map[file].append(info)

    def add_error_info(self, info: ErrorInfo) -> None:
        self._add_error_info(info.file, info)
    def file_messages(self, path: str) -> list[str]:
        if path not in self.error_info_map:
            return []
        self.flushed_files.add(path)
        return self.format_messages(self.error_info_map[path])
    def format_messages( self, error_info: list[ErrorInfo]) -> list[str]:
        a: list[str] = []
        for e in error_info:
            s = ""
            if e.file is not None:
                if e.line >= 0 and e.column >= 0:
                    srcloc = f"{e.file}:{e.line}:{1 + e.column}"
                    if e.end_line >= 0 and e.end_column >= 0:
                        srcloc += f":{e.end_line}:{e.end_column}"
                elif e.line >= 0:
                    srcloc = f"{e.file}:{e.line}"
                else:
                    srcloc = e.file
                s = f"{srcloc}: {e.message}"
            else:
                s = e.message
            a.append(s)
        return a
