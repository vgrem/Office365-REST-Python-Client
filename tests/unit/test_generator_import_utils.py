"""Offline tests for import collection and insertion helpers."""

from __future__ import annotations

import ast

from generator.builders.imports import (
    class_name_collides_with_import,
    drop_unused_type_checking,
    existing_import_names,
    insert_import,
    install_imports,
    make_import,
)


def test_existing_import_names_includes_type_checking_block() -> None:
    tree = ast.parse("from a import A\nimport b\nif TYPE_CHECKING:\n    from c import C\n")

    assert existing_import_names(tree) == {("a", "A"), ("b", None), ("c", "C")}


def test_insert_import_keeps_only_missing_names() -> None:
    tree = ast.parse("from a import A\n")
    existing = existing_import_names(tree)

    assert insert_import(tree, ast.parse("from a import A, B").body[0], existing, len(tree.body))
    assert ast.unparse(tree.body[-1]) == "from a import B"


def test_insert_import_preserves_alias() -> None:
    tree = ast.parse("")

    assert insert_import(tree, ast.parse("from dataclasses import field as field_").body[0], set(), 0)
    assert ast.unparse(tree.body[0]) == "from dataclasses import field as field_"


def test_install_imports_skips_already_present_names() -> None:
    tree = ast.parse("import os\n")
    existing = existing_import_names(tree)
    references = [ast.parse("import os").body[0], ast.parse("import sys").body[0]]

    inserted = install_imports(tree, references, existing, len(tree.body))

    assert [ast.unparse(node) for node in inserted] == ["import sys"]


def test_drop_unused_type_checking_removes_empty_block() -> None:
    tree = ast.parse("from typing import TYPE_CHECKING\n\n\nclass A:\n    pass\n")
    added = [tree.body[0]]

    kept = drop_unused_type_checking(tree, added)

    assert kept == []
    assert not any(isinstance(node, ast.ImportFrom) and node.module == "typing" for node in tree.body)


def test_drop_unused_type_checking_keeps_a_used_block() -> None:
    tree = ast.parse("from typing import TYPE_CHECKING\n\nif TYPE_CHECKING:\n    from a import A\n")
    added = [tree.body[0]]

    assert drop_unused_type_checking(tree, added) == added
    assert any(isinstance(node, ast.If) for node in tree.body)


def test_class_name_collides_with_import() -> None:
    tree = ast.parse("from a import Thing\n")

    assert class_name_collides_with_import(tree, "Thing")
    assert not class_name_collides_with_import(tree, "Other")


def test_make_import_sorts_names() -> None:
    assert ast.unparse(make_import("a", ["b", "a"])) == "from a import a, b"
