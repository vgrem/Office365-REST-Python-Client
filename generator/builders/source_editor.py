"""AST/text surgery for splicing new members into an existing module.

Isolated from :class:`~generator.builders.type.TypeBuilder` so the fragile,
line-index-based edits live in one place and can be unit-tested directly.
``TypeBuilder.render`` delegates here when the target file already exists.
"""

from __future__ import annotations

import ast
import copy
from dataclasses import dataclass
from typing import Optional

from generator.builders.render import normalize_quotes

#: Line length enforced by ruff; long import lines get an explicit noqa comment.
_MAX_LINE = 121

#: Annotation names that may also be bound as a module in the target file.
_MODULE_QUALIFIED = ("datetime", "date", "time")


def suppress_long_imports(source: str) -> str:
    """Append ``# noqa: E501`` to import lines longer than the limit (applied last)."""
    lines = [
        line + "  # noqa: E501"
        if len(line) > _MAX_LINE and line.lstrip().startswith(("from ", "import ")) and "noqa" not in line
        else line
        for line in source.splitlines()
    ]
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def is_type_checking(node: ast.If) -> bool:
    """Whether an ``if`` tests ``TYPE_CHECKING``."""
    test = node.test
    return (isinstance(test, ast.Name) and test.id == "TYPE_CHECKING") or (
        isinstance(test, ast.Attribute) and test.attr == "TYPE_CHECKING"
    )


def has_future_annotations(tree: ast.Module) -> bool:
    """Whether the module already imports ``from __future__ import annotations``."""
    return any(
        isinstance(node, ast.ImportFrom)
        and node.module == "__future__"
        and any(alias.name == "annotations" for alias in node.names)
        for node in tree.body
    )


def module_bound_names(tree: ast.Module) -> set[str]:
    """Names in ``{datetime, date, time}`` that the file imports as a module."""
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                base = alias.name.split(".")[0]
                if base in _MODULE_QUALIFIED:
                    names.add(base)
    return names


def strip_module_names(imports: list[ast.stmt], names: set[str]) -> list[ast.stmt]:
    """Drop ``from datetime import X`` names the file already binds as a module."""
    result: list[ast.stmt] = []
    for node in imports:
        stripped = node
        if isinstance(node, ast.ImportFrom) and node.module == "datetime":
            kept = [alias for alias in node.names if alias.name not in names]
            if not kept:
                continue
            stripped = ast.ImportFrom(module=node.module, names=kept, level=0)
        result.append(stripped)
    return result


class _ModuleQualifier(ast.NodeTransformer):
    """Qualify generated primitive references as ``<qualifier>.<name>``."""

    def __init__(self, names: set[str], qualifier: str) -> None:
        self._names = names
        self._qualifier = qualifier

    def visit_Name(self, node: ast.Name):
        if isinstance(node.ctx, ast.Load) and node.id in self._names:
            return ast.copy_location(
                ast.Attribute(
                    value=ast.Name(id=self._qualifier, ctx=ast.Load()),
                    attr=node.id,
                    ctx=ast.Load(),
                ),
                node,
            )
        return node


def qualify_modules(node: ast.stmt, names: set[str], qualifier: str) -> ast.stmt:
    """Qualify references to ``names`` in ``node`` with ``qualifier``."""
    return _ModuleQualifier(names, qualifier).visit(copy.deepcopy(node))


def qualify_datetime(node: ast.stmt) -> ast.stmt:
    """Qualify references to ``datetime`` with the ``datetime`` module."""
    return qualify_modules(node, {"datetime"}, "datetime")


def render_member(node: ast.stmt) -> str:
    """Render a class member statement indented one level."""
    module = ast.Module(body=[node], type_ignores=[])
    ast.fix_missing_locations(module)
    code = normalize_quotes(ast.unparse(module))
    return "\n".join("    " + line if line.strip() else line for line in code.splitlines())


@dataclass
class SourceEditor:
    """Splice members/imports into an existing module's **source text**.

    The original text is kept verbatim (comments, ``# type: ignore`` and hand
    formatting survive); only the new members and imports are inserted. Python's
    ``ast`` line numbers drive the insertion points, so edits are applied
    bottom-up to keep earlier line numbers valid.
    """

    text: str
    class_name: str

    def splice(self, members: list[ast.stmt], imports: list[ast.stmt], *, add_dataclass: bool = False) -> str:
        """Return the source with ``members``/``imports`` spliced in."""
        tree = ast.parse(self.text)
        members, imports = self._qualify(members, imports, tree)
        runtime_lines, type_checking_lines = self._split_imports(imports)
        return self._assemble(tree, members, runtime_lines, type_checking_lines, add_dataclass)

    @staticmethod
    def _qualify(
        members: list[ast.stmt], imports: list[ast.stmt], tree: ast.Module
    ) -> tuple[list[ast.stmt], list[ast.stmt]]:
        module_names = module_bound_names(tree)
        if not module_names:
            return list(members), list(imports)
        # The file binds these names as modules (``import time``); drop the
        # clashing ``from datetime import X`` and qualify generated refs.
        imports = strip_module_names(list(imports), module_names)
        qualifier = "datetime" if "datetime" in module_names else "_dt"
        if qualifier == "_dt":
            imports = [*imports, ast.Import(names=[ast.alias(name="datetime", asname="_dt")])]
        members = [qualify_modules(node, module_names, qualifier) for node in members]
        return members, imports

    @staticmethod
    def _split_imports(imports: list[ast.stmt]) -> tuple[list[str], list[str]]:
        runtime: list[str] = []
        type_checking: list[str] = []
        for imp in imports:
            if isinstance(imp, ast.If) and is_type_checking(imp):
                type_checking.extend(ast.unparse(stmt) for stmt in imp.body)
            else:
                runtime.append(ast.unparse(imp))
        return runtime, type_checking

    def _assemble(
        self,
        tree: ast.Module,
        members: list[ast.stmt],
        runtime_lines: list[str],
        type_checking_lines: list[str],
        add_dataclass: bool,
    ) -> str:
        lines = self.text.splitlines()
        class_end = self._class_body_end_line(tree)
        runtime_insert = self._last_runtime_import_line(tree)
        tc_block = self._find_type_checking_block(tree)

        if members:
            pass_line = self._sole_pass_line(tree)
            if pass_line is not None:
                del lines[pass_line - 1]
                class_end -= 1
            body = "\n\n".join(render_member(node) for node in members)
            lines[class_end:class_end] = ["", *body.splitlines()]
            if add_dataclass and not self._has_dataclass_decorator(tree):
                class_line = self._class_line(tree)
                if class_line is not None:
                    lines.insert(class_line, "@dataclass")

        if type_checking_lines:
            if tc_block is not None and tc_block.end_lineno is not None:
                lines[tc_block.end_lineno : tc_block.end_lineno] = ["    " + line for line in type_checking_lines]
            else:
                block = ["if TYPE_CHECKING:", *("    " + line for line in type_checking_lines)]
                lines[runtime_insert:runtime_insert] = block

        if runtime_lines:
            lines[runtime_insert:runtime_insert] = runtime_lines

        if members and not has_future_annotations(tree):
            # PEP 585 annotations (list[X]) need the future import on the py38 target.
            lines[0:0] = ["from __future__ import annotations", ""]

        return "\n".join(lines) + ("\n" if self.text.endswith("\n") else "")

    def _class_line(self, tree: ast.Module) -> Optional[int]:
        """0-based line index of the ``class <name>`` statement."""
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == self.class_name:
                return node.lineno - 1
        return None

    def _has_dataclass_decorator(self, tree: ast.Module) -> bool:
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == self.class_name:
                return any(isinstance(d, ast.Name) and d.id == "dataclass" for d in node.decorator_list)
        return False

    def _sole_pass_line(self, tree: ast.Module) -> Optional[int]:
        """Line of a ``pass`` that is the only statement in the target class body."""
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == self.class_name:
                if len(node.body) == 1 and isinstance(node.body[0], ast.Pass):
                    return node.body[0].lineno
        return None

    def _class_body_end_line(self, tree: ast.Module) -> int:
        """End line of the target class body (a module may hold several classes)."""
        first: Optional[ast.ClassDef] = None
        for node in tree.body:
            if not isinstance(node, ast.ClassDef):
                continue
            if first is None:
                first = node
            if node.name == self.class_name:
                last = node.body[-1]
                return last.end_lineno or last.lineno
        if first is not None:
            last = first.body[-1]
            return last.end_lineno or last.lineno
        return len(tree.body)

    @staticmethod
    def _last_runtime_import_line(tree: ast.Module) -> int:
        line = 0
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                line = node.end_lineno or line
        return line

    @staticmethod
    def _find_type_checking_block(tree: ast.Module) -> Optional[ast.If]:
        for node in tree.body:
            if isinstance(node, ast.If) and is_type_checking(node):
                return node
        return None
