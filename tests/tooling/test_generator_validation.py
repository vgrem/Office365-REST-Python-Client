"""Offline tests for post-generation validation."""

from __future__ import annotations

from generator.validation import validate_source


def test_clean_source_has_no_issues():
    source = "class A:\n    def x(self):\n        return 1\n"
    assert validate_source(source) == []


def test_duplicate_class_definition_detected():
    source = "class A:\n    pass\n\n\nclass A:\n    pass\n"
    assert any("duplicate class" in issue for issue in validate_source(source))


def test_duplicate_member_detected():
    source = "class A:\n    def x(self):\n        return 1\n\n    def x(self):\n        return 2\n"
    assert any("duplicate member" in issue for issue in validate_source(source))


def test_property_setter_is_not_a_duplicate():
    source = (
        "class A:\n"
        "    @property\n"
        "    def x(self):\n"
        "        return self._x\n\n"
        "    @x.setter\n"
        "    def x(self, value):\n"
        "        self._x = value\n"
    )
    assert validate_source(source) == []


def test_syntax_error_detected():
    assert validate_source("class A(:\n    pass\n") != []


def test_overloads_are_not_duplicates():
    source = (
        "from typing import overload\n"
        "class A:\n"
        "    @overload\n"
        "    def x(self, n: int) -> int: ...\n"
        "    @overload\n"
        "    def x(self, n: str) -> str: ...\n"
        "    def x(self, n):\n"
        "        return n\n"
    )
    assert validate_source(source) == []
