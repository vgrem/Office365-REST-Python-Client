"""Static ``OData type -> module`` index built from source (no imports).

Resolving by *class name* alone is ambiguous: ``SP.User`` and ``SP.Directory.User``
are both classes named ``User``. The index therefore keys classes by their
``entity_type_name`` (the authoritative OData name), falling back to the default
``"<namespace>.<ClassName>"`` when a class relies on the base implementation, and
only then to the bare class name.

Scanning is pure AST — no module is imported — so cyclic entity graphs cannot
make resolution fail or become order-dependent.
"""

from __future__ import annotations

import ast
import importlib.util
from pathlib import Path
from typing import Iterable, Optional

from office365.runtime.odata.type import ODataType


class SymbolIndex:
    """Maps OData type names (and bare class names) to their defining module.

    Built from one or more package roots (e.g. ``office365.sharepoint``).
    """

    def __init__(self, modules: Iterable[str], namespace: str = "") -> None:
        self._namespace = namespace
        self._by_name: dict[str, list[str]] = {}
        self._by_odata: dict[str, list[tuple[str, str]]] = {}
        self._files: dict[tuple[str, str], str] = {}
        self._members_cache: dict[tuple[str, str], set[str]] = {}
        for module_name in modules:
            for root in self._package_dirs(module_name):
                self._scan_root(module_name, root)

    def resolve_module(self, type_name: str | None, *, strict: bool = False) -> Optional[str]:
        """The module that defines ``type_name`` (an OData name or bare class name).

        ``strict`` restricts resolution to the authoritative OData name (and the
        class name matching its short name); the bare-class-name fallback is only
        for best-effort annotation/import hints, never for update decisions.
        """
        if not type_name:
            return None
        key = ODataType.normalize_type_name(type_name) or type_name
        short = key.rsplit(".", 1)[-1]
        candidates = self._by_odata.get(key, [])
        for class_name, module in candidates:
            if class_name == short:
                return module
        if candidates:
            return candidates[0][1]
        if strict:
            return None
        modules = self._by_name.get(short, [])
        return modules[0] if modules else None

    def class_members(self, type_name: str | None) -> set[str]:
        """Member names a class already has (incl. inherited), purely from AST."""
        if not type_name:
            return set()
        module = self.resolve_module(type_name)
        if module is None:
            return set()
        class_name = (ODataType.normalize_type_name(type_name) or type_name).rsplit(".", 1)[-1]
        return self._members_of(module, class_name)

    def _members_of(self, module: str, class_name: str) -> set[str]:
        key = (module, class_name)
        if key in self._members_cache:
            return self._members_cache[key]
        self._members_cache[key] = set()  # break cycles while recursing
        names, bases = self._class_info(module, class_name)
        for base in bases:
            names |= self.class_members(base)
        self._members_cache[key] = names
        return names

    def _scan_root(self, module_name: str, root: str) -> None:
        for path in sorted(Path(root).rglob("*.py")):
            self._scan_file(module_name, Path(root), path)

    def _scan_file(self, module_name: str, root: Path, path: Path) -> None:
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        except (SyntaxError, OSError):
            return
        module_path = self._module_path(module_name, root, path)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            bucket = self._by_name.setdefault(node.name, [])
            if module_path not in bucket:
                bucket.append(module_path)
            self._files[(module_path, node.name)] = str(path)
            odata_name = self._entity_type_name(node) or (f"{self._namespace}.{node.name}" if self._namespace else "")
            if odata_name:
                key = ODataType.normalize_type_name(odata_name) or odata_name
                self._by_odata.setdefault(key, []).append((node.name, module_path))

    @staticmethod
    def _entity_type_name(node: ast.ClassDef) -> Optional[str]:
        """The literal returned by a class's own ``entity_type_name`` property."""
        for stmt in node.body:
            if isinstance(stmt, ast.FunctionDef) and stmt.name == "entity_type_name":
                for sub in ast.walk(stmt):
                    if (
                        isinstance(sub, ast.Return)
                        and isinstance(sub.value, ast.Constant)
                        and isinstance(sub.value.value, str)
                    ):
                        return sub.value.value
        return None

    def _class_info(self, module: str, class_name: str) -> tuple[set[str], list[str]]:
        path = self._files.get((module, class_name))
        if path is None:
            return set(), []
        try:
            tree = ast.parse(Path(path).read_text(encoding="utf-8"))
        except (SyntaxError, OSError):
            return set(), []
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                return self._member_names(node), self._base_names(node)
        return set(), []

    @staticmethod
    def _member_names(node: ast.ClassDef) -> set[str]:
        names: set[str] = set()
        for stmt in node.body:
            if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if any(_is_accessor(d) for d in stmt.decorator_list):
                    continue
                names.add(stmt.name)
            elif isinstance(stmt, ast.Assign):
                names.update(t.id for t in stmt.targets if isinstance(t, ast.Name))
            elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name):
                names.add(stmt.target.id)
        return names

    @staticmethod
    def _base_names(node: ast.ClassDef) -> list[str]:
        names: list[str] = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                names.append(base.id)
            elif isinstance(base, ast.Subscript) and isinstance(base.value, ast.Name):
                names.append(base.value.id)
        return names

    @staticmethod
    def _module_path(module_name: str, root: Path, path: Path) -> str:
        parts = list(path.relative_to(root).with_suffix("").parts)
        if parts and parts[-1] == "__init__":
            parts = parts[:-1]
        return ".".join([module_name, *parts]) if parts else module_name

    @staticmethod
    def _package_dirs(module_name: str) -> list[str]:
        try:
            spec = importlib.util.find_spec(module_name)
        except (ImportError, ValueError):
            return []
        return list(spec.submodule_search_locations or []) if spec is not None else []


def _is_accessor(decorator: ast.expr) -> bool:
    return isinstance(decorator, ast.Attribute) and decorator.attr in {"setter", "deleter", "getter"}
