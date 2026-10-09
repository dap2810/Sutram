#!/usr/bin/env python3
"""DEVELOPMENT/TEST REFERENCE ONLY for proposed Sutram module graph v1.

NOT imported by the Sutram compiler, NOT a compiler/runtime dependency.
This is an executable oracle specifying deterministic depth-first initialization
ordering, one-visit semantics, exact diagnostics, and explicit exports.  The
handwritten NASM compiler has not implemented this complete contract yet.
"""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import re

IMPORT_RE = re.compile(r'^\s*ayojan\s+([A-Za-z_][\w-]*)(?:@([A-Za-z_][\w]*))?\s*(?:#.*)?$')
EXPORT_RE = re.compile(r'^\s*niryat\s+([A-Za-z_][\w]*)\s*(?:#.*)?$')
FUNC_RE = re.compile(r'^\s*(?:prakriya|sutra)\s+([A-Za-z_][\w]*)\s*\(')

@dataclass(frozen=True)
class Import:
    module: str
    alias: str | None
    line: int

@dataclass
class Module:
    name: str
    path: Path
    imports: list[Import] = field(default_factory=list)
    exported: dict[str, int] = field(default_factory=dict)
    functions: dict[str, int] = field(default_factory=dict)
    explicit: bool = False

class GraphDiagnostic(Exception):
    def __init__(self, kind: str, path: Path, line: int, message: str):
        self.kind, self.path, self.line = kind, path, line
        self.message = f'{path}:{line}: Sutram Error [{kind}]: {message}'
        super().__init__(self.message)

class GraphReference:
    def __init__(self, root: Path):
        self.root = root
        self.modules: dict[str, Module] = {}
        self.state: dict[str, int] = {}  # 0 unseen, 1 visiting, 2 complete
        self.stack: list[str] = []
        self.order: list[str] = []
        self.import_map: dict[str, str] = {}

    def parse(self, module: str, importer: Path, line: int) -> Module:
        if module in self.modules:
            return self.modules[module]
        path = self.root / (module + '.smlib')
        if not path.is_file():
            raise GraphDiagnostic('E_MODULE_MISSING', importer, line,
                                  f'module {module!r} not found under {self.root}')
        m = Module(module, path)
        for index, raw in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            line_text = raw.split('#', 1)[0].rstrip()
            if index == 1 and raw.strip() == '# sutram-module-v1':
                m.explicit = True
            if not line_text.strip():
                continue
            im = IMPORT_RE.fullmatch(line_text)
            if im:
                m.imports.append(Import(im.group(1), im.group(2), index))
                continue
            em = EXPORT_RE.fullmatch(line_text)
            if em:
                if em.group(1) in m.exported:
                    raise GraphDiagnostic('E_EXPORT_DUPLICATE', path, index,
                                          f'duplicate export {em.group(1)!r}')
                m.exported[em.group(1)] = index
            fm = FUNC_RE.match(line_text)
            if fm:
                m.functions[fm.group(1)] = index
        if m.explicit:
            for name, n in m.exported.items():
                if name not in m.functions:
                    raise GraphDiagnostic('E_EXPORT_UNDEFINED', path, n,
                                          f'export {name!r} has no function definition')
        else:
            m.exported = dict(m.functions)  # legacy compatibility
        self.modules[module] = m
        return m

    def visit(self, module: str, importer: Path, line: int):
        state = self.state.get(module, 0)
        if state == 1:
            i = self.stack.index(module)
            cycle = ' -> '.join(self.stack[i:] + [module])
            raise GraphDiagnostic('E_MODULE_CYCLE', importer, line, cycle)
        if state == 2:
            return  # diamond deduplicated; no second init
        m = self.parse(module, importer, line)
        self.state[module] = 1
        self.stack.append(module)
        for imp in m.imports:
            self.visit(imp.module, m.path, imp.line)
        self.stack.pop()
        self.state[module] = 2
        self.order.append(module)  # imports before importer, siblings source order

    def analyze(self, entry: Path):
        self.modules.clear();self.state.clear();self.stack.clear();self.order.clear();self.import_map.clear()
        for num, raw in enumerate(entry.read_text(encoding='utf-8').splitlines(), 1):
            if raw.lstrip().startswith('#'):
                continue
            im = IMPORT_RE.fullmatch(raw.split('#', 1)[0].strip())
            if im:
                module, alias = im.group(1), im.group(2)
                key = alias or module
                if key in self.import_map and self.import_map[key] != module:
                    raise GraphDiagnostic('E_IMPORT_ALIAS', entry, num,
                                          f'import {key!r} refers to two different modules')
                self.import_map[key] = module
                self.visit(module, entry, num)
        # Opt-in modern entries cannot accept two unqualified exports with same name.
        if entry.read_text(encoding='utf-8').startswith('# sutram-module-v1'):
            names = {}
            for key, module in self.import_map.items():
                if key != module:  # named alias provides isolation
                    continue
                for exported in self.modules[module].exported:
                    if exported in names and names[exported] != module:
                        raise GraphDiagnostic('E_EXPORT_COLLISION', entry, 1,
                                              f'{exported!r} exported by {names[exported]} and {module}; use @alias')
                    names[exported] = module
        return self.order

    def check_access(self, module: str, function: str, importer: Path, line: int):
        m = self.modules[module]
        if function not in m.exported:
            raise GraphDiagnostic('E_PRIVATE_SYMBOL', importer, line,
                                  f'{module}.{function} is private; add niryat {function} to export it')
        return True
