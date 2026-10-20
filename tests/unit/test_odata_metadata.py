"""Generated getters declare their own OData metadata (wire name, navigation).

The wire name is a fact about the CSDL, not something derivable from the attribute
name: ``iCalUId`` and ``icalUid`` both round-trip through a snake-case guess, and
only one of them is a real column. These tests pin the declaration and the codemod
that back-filled it onto files the generator will not re-render.

Completeness is claimed per module, never globally: only the packages listed here
are expected to be fully marked.
"""

from __future__ import annotations

import pathlib
import shutil

import pytest
import scripts.mark_odata as codemod
from office365.outlook.calendar.events.event import Event
from office365.outlook.mail.messages.message import Message

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
#: Packages whose getters are expected to be fully declared today.
_SERVED = ("office365/outlook",)


def test_the_wire_name_of_ical_uid_survives_where_a_naming_inverse_would_fail():
    # to_snake_case("iCalUId") is i_cal_u_id while the getter is ical_uid, so only
    # the declaration can answer; the attribute tells the stack where to read it.
    assert Event._odata_meta["iCalUId"].attr == "ical_uid"


def test_navigation_properties_are_declared_as_such():
    # $select cannot name a navigation property, so it must be distinguishable.
    assert Event._odata_meta["calendar"].navigation is True
    assert Event._odata_meta["attachments"].navigation is True
    assert Event._odata_meta["singleValueExtendedProperties"].navigation is True
    assert Event._odata_meta["iCalUId"].navigation is False


def test_select_all_is_the_projection_the_declarations_describe():
    columns = Event.select_all()

    assert "iCalUId" in columns  # a column whose name a snake-case guess gets wrong
    assert "id" in columns  # inherited from Entity, so the base carries a declaration too
    assert "attachments" not in columns  # a navigation property: $select would reject it
    assert "calendar" not in columns
    assert len(columns) == len(set(columns))


def test_expandable_is_the_complement_of_select_all():
    expandable = Event.expandable()

    assert "singleValueExtendedProperties" in expandable
    assert "instances" in expandable
    assert "iCalUId" not in expandable
    assert not set(expandable) & set(Event.select_all())


def test_wire_name_answers_for_an_attribute_and_refuses_an_unknown_one():
    assert Event.wire_name("ical_uid") == "iCalUId"
    assert Message.wire_name("from_") == "from"  # a reserved word, renamed by the generator
    # A naming inverse would happily answer i_cal_u_id here; the declaration knows better.
    with pytest.raises(AttributeError, match="not a declared property"):
        Event.wire_name("i_cal_u_id")


def test_select_all_names_a_column_once():
    # "from" is read by one getter whose name carries a trailing underscore; a
    # projection must not repeat it if another getter ever reads the same name.
    assert Message.select_all().count("from") == 1


def test_no_served_module_has_an_undeclared_wire_name_left():
    catalog = codemod.load_catalog()
    for root in _SERVED:
        for path in sorted((_REPO_ROOT / root).rglob("*.py")):
            assert codemod.plan_module(path, catalog) == [], f"{path} still needs declarations"


def test_the_codemod_finishes_a_marker_that_names_a_navigation_property(tmp_path):
    # The first pass only added declarations, so every marker it wrote to a file that
    # already had one stayed half-written: the name, without the navigation flag.
    target = tmp_path / "event.py"
    target.write_text(
        "from office365.runtime.types.odata_property import odata\n"
        "\n"
        "\n"
        "class Event:\n"
        '    @odata(name="singleValueExtendedProperties")\n'
        "    @property\n"
        "    def single_value_extended_properties(self) -> None:\n"
        '        return self.properties.get("singleValueExtendedProperties", None)\n'
        "\n"
        "    @property\n"
        "    def entity_type_name(self) -> str:\n"
        '        return "microsoft.graph.Event"\n',
        encoding="utf-8",
    )

    assert codemod.mark_module(target, codemod.load_catalog()) == 1
    assert '@odata(name="singleValueExtendedProperties", navigation=True)' in target.read_text(encoding="utf-8")
    # Idempotent: a finished marker is not touched again.
    assert codemod.mark_module(target, codemod.load_catalog()) == 0


def test_the_codemod_leaves_a_marked_module_alone(tmp_path):
    source = _REPO_ROOT / "office365" / "outlook" / "contacts" / "contact.py"
    target = tmp_path / source.name
    shutil.copy(source, target)

    assert codemod.mark_module(target, codemod.load_catalog()) == 0  # already marked
    assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
