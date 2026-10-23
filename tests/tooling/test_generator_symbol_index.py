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
    _write(root / "pkg/todo/tasks/task.py", "from pkg.entity import Entity\n\n\nclass TodoTask(Entity):\n    pass\n")


def _build_field_collision(root: Path) -> None:
    for package in ("pkg", "pkg/fields", "pkg/listitems/caml"):
        _write(root / package / "__init__.py", "")
    # The model module the generator owns: a plural directory naming the type.
    _write(root / "pkg/fields/field.py", "from pkg.entity import Entity\n\n\nclass Field(Entity):\n    pass\n")
    # A hand-written DSL class that happens to share the name and claims
    # ``SP.Field`` through the ``<namespace>.<ClassName>`` fallback.
    _write(root / "pkg/listitems/caml/expressions.py", "class Field:\n    pass\n")


def test_hand_written_helper_does_not_shadow_the_model_module(tmp_path: Path, monkeypatch) -> None:
    _build_field_collision(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    index = SymbolIndex(["pkg"], namespace="SP")

    assert index.resolve_module("SP.Field", strict=True) == "pkg.fields.field"


def _build_package_collision(root: Path) -> None:
    for package in ("pkg", "pkg/driveitems", "pkg/migration/package"):
        _write(root / package / "__init__.py", "")
    _write(
        root / "pkg/driveitems/package.py",
        "from pkg.client_value import ClientValue\n\n\nclass Package(ClientValue):\n    pass\n",
    )
    # A hand-written helper that shares the class name and has no base classes:
    # it is not a model type, so it must not claim ``microsoft.graph.Package``.
    _write(root / "pkg/migration/package/builder.py", "class Package:\n    type: str | None = None\n")


def test_class_without_base_does_not_claim_a_model_type(tmp_path: Path, monkeypatch) -> None:
    _build_package_collision(tmp_path)
    monkeypatch.syspath_prepend(str(tmp_path))

    index = SymbolIndex(["pkg"], namespace="microsoft.graph")

    assert index.resolve_module("microsoft.graph.Package", strict=True, kind="ComplexType") == "pkg.driveitems.package"
    assert "microsoft.graph.Package" not in index.duplicate_types()


def test_declared_entity_type_name_is_honoured_without_a_base(tmp_path: Path, monkeypatch) -> None:
    for package in ("pkg", "pkg/calendar"):
        _write(tmp_path / package / "__init__.py", "")
    # Enum types in the metadata are declared without a Python base: the
    # declared entity_type_name is then the only signal, so honour it.
    _write(
        tmp_path / "pkg/calendar/activity_domain.py",
        "class ActivityDomain:\n"
        "    @property\n"
        "    def entity_type_name(self) -> str:\n"
        '        return "microsoft.graph.ActivityDomain"\n',
    )
    monkeypatch.syspath_prepend(str(tmp_path))

    index = SymbolIndex(["pkg"], namespace="microsoft.graph")

    assert index.resolve_module("microsoft.graph.ActivityDomain", strict=True) == "pkg.calendar.activity_domain"


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
