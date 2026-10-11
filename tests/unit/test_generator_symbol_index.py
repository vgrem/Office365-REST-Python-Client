"""Offline tests for the OData name -> module index (duplicate handling).

A generated duplicate parked in the shared bucket must never shadow the real
product module, regardless of scan order.
"""

from __future__ import annotations

from pathlib import Path

from generator.builders.symbol_index import SymbolIndex


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _build_package(root: Path) -> None:
    for package in ("pkg", "pkg/common", "pkg/todo", "pkg/todo/tasks"):
        _write(root / package / "__init__.py", "")
    # A stale duplicate in the shared bucket with an explicit entity_type_name.
    _write(
        root / "pkg/common/todo_task.py",
        "class TodoTask:\n"
        "    @property\n"
        "    def entity_type_name(self) -> str:\n"
        '        return "microsoft.graph.TodoTask"\n',
    )
    # The real product module, which omits entity_type_name.
    _write(
        root / "pkg/todo/tasks/task.py",
        "class TodoTask:\n    @property\n    def entity_type_name(self) -> str:\n        return None  # type: ignore\n",
    )


def test_common_duplicate_does_not_shadow_the_product_module(tmp_path: Path, monkeypatch) -> None:
    _build_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    index = SymbolIndex(["pkg.common", "pkg.todo"], namespace="microsoft.graph")

    assert index.resolve_module("microsoft.graph.TodoTask", strict=True) == "pkg.todo.tasks.task"


def test_duplicate_types_reports_names_owned_by_several_modules(tmp_path: Path, monkeypatch) -> None:
    _build_package(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    index = SymbolIndex(["pkg.common", "pkg.todo"], namespace="microsoft.graph")

    assert index.duplicate_types() == {
        "microsoft.graph.TodoTask": ["pkg.common.todo_task", "pkg.todo.tasks.task"],
    }
