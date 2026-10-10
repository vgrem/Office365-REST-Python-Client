"""Offline tests for the source editor (splicing into existing files)."""

from __future__ import annotations

import ast

from generator.builders.source_editor import (
    SourceEditor,
    has_future_annotations,
    is_type_checking,
    module_bound_names,
    qualify_datetime,
    strip_module_names,
    suppress_long_imports,
)


def _stmt(code: str) -> ast.stmt:
    return ast.parse(code).body[0]


def test_suppress_long_imports_only_touches_long_import_lines() -> None:
    source = "from a import b\n" + "from a_very_long_module_name_that_exceeds_the_limit import " + "x" * 120 + "\n"

    out = suppress_long_imports(source).splitlines()

    assert out[0] == "from a import b"
    assert out[1].endswith("# noqa: E501")


def test_is_type_checking_variants() -> None:
    assert is_type_checking(_stmt("if TYPE_CHECKING:\n    pass"))
    assert is_type_checking(_stmt("if typing.TYPE_CHECKING:\n    pass"))
    assert not is_type_checking(_stmt("if x:\n    pass"))


def test_has_future_annotations() -> None:
    assert has_future_annotations(ast.parse("from __future__ import annotations\n"))
    assert not has_future_annotations(ast.parse("x = 1\n"))


def test_qualify_datetime() -> None:
    assert "datetime.datetime" in ast.unparse(qualify_datetime(_stmt("def f(x: datetime) -> None: ...")))


def test_module_bound_names_and_strip() -> None:
    tree = ast.parse("import time\nfrom datetime import datetime, date\n")

    assert module_bound_names(tree) == {"time"}
    imports = [node for node in tree.body if isinstance(node, ast.ImportFrom)]
    assert ast.unparse(strip_module_names(imports, {"time", "date"})[0]) == "from datetime import datetime"


def test_splice_inserts_member_and_preserves_comments() -> None:
    original = (
        "from __future__ import annotations\n"
        "\n"
        "from office365.runtime.client_value import ClientValue\n"
        "\n"
        "\n"
        "@dataclass\n"
        "class Thing(ClientValue):\n"
        "    # keep me\n"
        "    existing: str | None = None\n"
    )

    out = SourceEditor(original, "Thing").splice([_stmt("new: int | None = None")], [])

    assert "# keep me" in out
    assert "new: int | None = None" in out
    ast.parse(out)


def test_splice_drops_sole_pass() -> None:
    out = SourceEditor("from enum import Enum\n\n\nclass E(Enum):\n    pass\n", "E").splice([_stmt("a = 1")], [])

    assert "pass" not in out
    assert "a = 1" in out
    ast.parse(out)


def test_splice_adds_dataclass_decorator_when_requested() -> None:
    out = SourceEditor("class Thing:\n    existing = 1\n", "Thing").splice([_stmt("new = 2")], [], add_dataclass=True)

    assert "@dataclass" in out
    ast.parse(out)


def test_splice_adds_future_annotations_when_missing() -> None:
    out = SourceEditor("class Thing:\n    existing = 1\n", "Thing").splice([_stmt("new = 2")], [])

    assert out.startswith("from __future__ import annotations")
    ast.parse(out)


def test_splice_inserts_runtime_import_after_last_import() -> None:
    out = SourceEditor("import os\n\n\nclass Thing:\n    existing = 1\n", "Thing").splice(
        [_stmt("new = 2")], [_stmt("import sys")]
    )

    lines = out.splitlines()
    assert lines.index("import sys") > lines.index("import os")
    ast.parse(out)


def test_splice_extends_existing_type_checking_block() -> None:
    original = (
        "from typing import TYPE_CHECKING\n"
        "\n"
        "if TYPE_CHECKING:\n"
        "    from a import A\n"
        "\n"
        "\n"
        "class Thing:\n"
        "    existing = 1\n"
    )
    out = SourceEditor(original, "Thing").splice([_stmt("new = 2")], [_stmt("if TYPE_CHECKING:\n    from b import B")])

    assert "from b import B" in out
    assert "from a import A" in out
    ast.parse(out)
