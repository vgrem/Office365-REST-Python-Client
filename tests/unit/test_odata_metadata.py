"""Generated getters declare their own OData metadata (wire name, navigation).

The wire name is a fact about the CSDL, not something derivable from the attribute
name: ``iCalUId`` and ``icalUid`` both round-trip through a snake-case guess, and
only one of them is a real column. These tests pin the declaration and the codemod
that back-filled it onto files the generator will not re-render.

Completeness is claimed per module, never globally: only the packages listed here
are expected to be fully marked.
"""

from __future__ import annotations

import importlib
import pathlib
import pkgutil
import shutil
from dataclasses import dataclass, field
from datetime import datetime

import pytest
import scripts.mark_odata as codemod
from office365.communications.onlinemeetings.online_meeting_info import OnlineMeetingInfo
from office365.directory.identity_set import IdentitySet
from office365.directory.permissions.identity import Identity
from office365.outlook.calendar.dateTimeTimeZone import DateTimeTimeZone
from office365.outlook.calendar.events.event import Event
from office365.outlook.mail.messages.message import Message
from office365.planner.assignment import PlannerAssignment
from office365.runtime.client_object import ClientObject
from office365.runtime.client_value import ClientValue
from office365.runtime.converters.value import declared_type
from office365.runtime.odata.v4.json_format import V4JsonFormat
from office365.runtime.types.odata_property import _ODATA_MARKER, ODataPropertyMeta, field_declarations, odata

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


def test_no_served_module_has_a_column_without_a_declared_type():
    # A $select answers only the columns it names, so a column whose type does not
    # resolve hydrates a bare dict where the model promises a value object.
    untyped = []
    for root in _SERVED:
        package = root.replace("/", ".")
        for info in pkgutil.walk_packages([str(_REPO_ROOT / root)], prefix=f"{package}."):
            module = importlib.import_module(info.name)
            for cls in _entity_types(module):
                for name in cls.select_all():
                    if declared_type(cls, name) is None:
                        untyped.append(f"{cls.__module__}.{cls.__name__}.{name}")
    assert untyped == []


def _entity_types(module):
    for member in vars(module).values():
        if isinstance(member, type) and issubclass(member, ClientObject) and member.__module__ == module.__name__:
            yield member


def test_a_nested_column_declares_the_type_its_getter_returns():
    # These getters construct the type at runtime but used to leave the return
    # annotation off, so a declared column resolved to None.
    assert declared_type(Event, "start") is DateTimeTimeZone
    assert declared_type(Event, "end") is DateTimeTimeZone
    assert declared_type(Event, "onlineMeeting") is OnlineMeetingInfo
    assert declared_type(Event, "attendees") is not None


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


def test_one_declaration_serves_a_property_and_a_dataclass_field():
    # A ClientValue is a dataclass, so it has fields where a ClientObject has
    # properties. The fact is the same one -- the JSON key, and who owns the value --
    # so the declaration is the same: callable for a property, a Mapping for a field.
    declaration = odata(name="assignedDateTime", readonly=True)
    assert declaration[_ODATA_MARKER].name == "assignedDateTime"
    assert declaration[_ODATA_MARKER].readonly is True

    @dataclass
    class Draft(ClientValue):
        assigned_date_time: str | None = field(default=None, metadata=odata(name="assignedDateTime"))

    declared = Draft.__dataclass_fields__["assigned_date_time"].metadata[_ODATA_MARKER]
    assert isinstance(declared, ODataPropertyMeta)
    assert declared.name == "assignedDateTime"


def test_a_nested_field_declares_who_owns_its_value():
    # Planner's to_json overrides existed to pop the two fields Graph fills in and
    # rejects on write. The declaration says it once, and both profiles follow it:
    # a response carries what the service said, a request cannot claim it.
    assignment = PlannerAssignment(
        assignedBy=IdentitySet(user=Identity(displayName="Ann", id="1")),
        assignedDateTime=datetime(2026, 3, 9, 9, 0),
        orderHint=" !",
    )
    assert set(assignment.to_json()) == {"assignedBy", "assignedDateTime", "orderHint"}
    assert assignment.to_json(V4JsonFormat("none")) == {"orderHint": " !"}


def test_declaring_a_nested_field_is_opt_in():
    declared = field_declarations(PlannerAssignment)
    assert declared["assignedBy"].readonly is True
    assert declared["assignedBy"].name == "assignedBy"
    assert "orderHint" not in declared  # undeclared fields keep their own name
    assert field_declarations(IdentitySet) == {}  # 2,887 nested types are untouched


def test_the_decorator_carrier_attaches_the_same_metadata():
    # 892 getters are declared this way; the Mapping form must not have changed it.
    class Thing:
        @odata(name="iCalUId", readonly=True)
        def ical_uid(self): ...

    assert getattr(Thing.ical_uid, _ODATA_MARKER) == ODataPropertyMeta(name="iCalUId", readonly=True)


def test_the_codemod_leaves_a_marked_module_alone(tmp_path):
    source = _REPO_ROOT / "office365" / "outlook" / "contacts" / "contact.py"
    target = tmp_path / source.name
    shutil.copy(source, target)

    assert codemod.mark_module(target, codemod.load_catalog()) == 0  # already marked
    assert target.read_text(encoding="utf-8") == source.read_text(encoding="utf-8")
