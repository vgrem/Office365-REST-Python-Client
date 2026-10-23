"""Offline tests for generated-source post-processing (quote normalization)."""

from __future__ import annotations

import ast

from generator.builders.render import normalize_quotes


def test_normalizes_to_double_quotes():
    assert normalize_quotes("x = self.properties.get('Title', None)\n") == 'x = self.properties.get("Title", None)\n'


def test_keeps_single_quotes_when_value_contains_double_quote():
    source = "x = 'say \"hi\"'\n"
    assert normalize_quotes(source) == source


def test_preserves_docstrings():
    source = 'def f():\n    """a "doc" """\n    return 1\n'
    assert normalize_quotes(source) == source


def test_output_still_parses():
    source = "x = {'a': 1, 'b': 'it\\'s'}\n"
    assert ast.parse(normalize_quotes(source)) is not None
