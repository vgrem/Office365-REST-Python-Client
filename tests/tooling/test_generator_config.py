"""Offline tests for YAML config loading and validation."""

from __future__ import annotations

from pathlib import Path

import pytest
from generator.config import ConfigError, GeneratorOptions, parse_list, split_ignored

_BASE = """
metadata_path: ./metadata/Graph.xml
output_path: ./office365
template_path: ./templates
modules: [office365]
"""


def _write(tmp_path: Path, body: str) -> None:
    (tmp_path / "templates").mkdir(exist_ok=True)
    (tmp_path / "office365").mkdir(exist_ok=True)
    (tmp_path / "settings.graph.yaml").write_text(body, encoding="utf-8")


def test_load_reads_typed_options(tmp_path: Path) -> None:
    _write(
        tmp_path,
        _BASE
        + """
context_type: GraphClient
generate_methods: true
include_base_types: [ComplexType, EnumType]
filters:
  ignored_types: [microsoft.graph.X, "microsoft.graph.Edu*"]
routing:
  microsoft.graph.foo: office365.foo
type_routing:
  "Bar*": office365.bar
""",
    )

    options = GeneratorOptions.load("graph", tmp_path)

    assert options.include_base_types == ["ComplexType", "EnumType"]
    assert options.generate_methods == "true"
    assert options.ignored_types == ["microsoft.graph.X", "microsoft.graph.Edu*"]
    assert options.routing == {"microsoft.graph.foo": "office365.foo"}
    assert options.type_routing == {"Bar*": "office365.bar"}
    assert options.template_path == str((tmp_path / "templates").resolve())


def test_missing_config_file(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="missing config"):
        GeneratorOptions.load("graph", tmp_path)


def test_unknown_top_level_key(tmp_path: Path) -> None:
    _write(tmp_path, _BASE + "bogus: 1\n")
    with pytest.raises(ConfigError, match="unknown key"):
        GeneratorOptions.load("graph", tmp_path)


def test_missing_required_key(tmp_path: Path) -> None:
    _write(tmp_path, "metadata_path: ./m.xml\ntemplate_path: ./templates\n")
    with pytest.raises(ConfigError, match="missing required key 'output_path'"):
        GeneratorOptions.load("graph", tmp_path)


def test_unknown_filter_key(tmp_path: Path) -> None:
    _write(tmp_path, _BASE + "filters:\n  bogus: []\n")
    with pytest.raises(ConfigError, match="unknown filter key"):
        GeneratorOptions.load("graph", tmp_path)


def test_template_path_must_exist(tmp_path: Path) -> None:
    (tmp_path / "office365").mkdir()
    (tmp_path / "settings.graph.yaml").write_text(_BASE.replace("./templates", "./nope"), encoding="utf-8")
    with pytest.raises(ConfigError, match="template_path is not a directory"):
        GeneratorOptions.load("graph", tmp_path)


def test_scanned_module_must_exist(tmp_path: Path) -> None:
    _write(tmp_path, _BASE.replace("modules: [office365]", "modules: [office365.missing]"))
    with pytest.raises(ConfigError, match="has no directory"):
        GeneratorOptions.load("graph", tmp_path)


def test_invalid_yaml(tmp_path: Path) -> None:
    _write(tmp_path, "metadata_path: [unclosed\n")
    with pytest.raises(ConfigError, match="invalid YAML"):
        GeneratorOptions.load("graph", tmp_path)


def test_parse_list_accepts_lists_strings_and_none() -> None:
    assert parse_list(["a", " b "]) == ["a", "b"]
    assert parse_list("a, b\nc") == ["a", "b", "c"]
    assert parse_list(None) == []


def test_split_ignored_separates_prefix_patterns() -> None:
    assert split_ignored(["X", "Edu*"]) == (["X"], ["Edu"])
