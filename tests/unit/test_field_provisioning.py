"""Offline tests for rich field provisioning.

``List.ensure_field`` / ``ensure_fields`` accept rich
:class:`FieldCreationInformation` specs (choices, formula, required, ...), and
``FieldCollection.ensure(..., on_conflict="update")`` reconciles those rich
settings on an existing column. Everything stays deferred — no request is sent
until ``execute_query()``.
"""

from __future__ import annotations

from office365.runtime.http.http_method import HttpMethod
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.fields.creation_information import FieldCreationInformation
from office365.sharepoint.fields.field import Field
from office365.sharepoint.fields.type import FieldType
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _sp(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport(payloads)
    ctx.pending_request().transport = transport
    return ctx, transport


def _existing(**props):
    return {"d": props}


# --- declarative rich specs (deferred) ---------------------------------------


def test_ensure_fields_accepts_rich_specs_deferred():
    ctx, transport = _sp([])

    fields = ctx.web.lists.get_by_title("Tasks").ensure_fields(
        [
            FieldCreationInformation(Title="Status", FieldTypeKind=FieldType.Choice, Choices=["A", "B"]),
            FieldCreationInformation(Title="Budget", FieldTypeKind=FieldType.Number),
        ]
    )

    assert transport.calls == 0
    assert len(fields) == 2  # noqa: PLR2004
    assert all(isinstance(field, Field) for field in fields)
    urls = " ".join(field.resource_url for field in fields)
    assert "getByTitle('Status')" in urls
    assert "getByTitle('Budget')" in urls


def test_ensure_fields_accepts_names_and_mapping():
    ctx, transport = _sp([])
    lst = ctx.web.lists.get_by_title("Tasks")

    by_name = lst.ensure_fields(["A", "B"])
    by_type = lst.ensure_fields({"C": FieldType.Number})

    assert transport.calls == 0
    assert len(by_name) == 2  # noqa: PLR2004
    assert len(by_type) == 1
    assert all(isinstance(field, Field) for field in by_name + by_type)


def test_ensure_field_accepts_field_creation_information():
    ctx, transport = _sp([])

    field = ctx.web.lists.get_by_title("Tasks").ensure_field(
        FieldCreationInformation(Title="Stage", FieldTypeKind=FieldType.Choice, Choices=["A"])
    )

    assert isinstance(field, Field)
    assert transport.calls == 0
    assert "getByTitle('Stage')" in field.resource_url


# --- rich reconcile on conflict ----------------------------------------------


def test_ensure_reconciles_choices_on_conflict_update():
    ctx, transport = _sp(
        [
            _existing(Title="Status", InternalName="Status", FieldTypeKind=6, Choices={"results": ["A", "B"]}),
            {},
        ]
    )

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Status", FieldTypeKind=FieldType.Choice, Choices=["A", "C"]),
            on_conflict="update",
        )
        .execute_query()
    )

    assert transport.calls == 2  # noqa: PLR2004
    assert list(field.choices) == ["A", "C"]
    # the reconcile patches the field entity itself, not the collection
    assert transport.requests[-1].method == HttpMethod.Post
    assert transport.requests[-1].headers.get("X-HTTP-Method") == "MERGE"
    assert transport.requests[-1].url.endswith("Fields/getByTitle('Status')")


def test_ensure_skip_keeps_existing_rich_settings():
    ctx, transport = _sp([_existing(Title="Status", FieldTypeKind=6, Choices={"results": ["A", "B"]})])

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Status", FieldTypeKind=FieldType.Choice, Choices=["A", "C"]),
        )
        .execute_query()
    )

    assert transport.calls == 1
    assert list(field.choices) == ["A", "B"]


def test_ensure_reconciles_formula_for_calculated():
    ctx, transport = _sp([_existing(Title="Total", FieldTypeKind=17, Formula="=1"), {}])

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Total", FieldTypeKind=FieldType.Calculated, Formula="=2"),
            on_conflict="update",
        )
        .execute_query()
    )

    assert transport.calls == 2  # noqa: PLR2004
    assert field.formula == "=2"


def test_ensure_turns_on_required():
    ctx, transport = _sp([_existing(Title="Owner", FieldTypeKind=2, Required=False), {}])

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Owner", FieldTypeKind=FieldType.Text, Required=True),
            on_conflict="update",
        )
        .execute_query()
    )

    assert transport.calls == 2  # noqa: PLR2004
    assert field.properties.get("Required") is True


def test_ensure_never_relaxes_required_by_default():
    ctx, transport = _sp([_existing(Title="Owner", FieldTypeKind=2, Required=True)])

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Owner", FieldTypeKind=FieldType.Text),
            on_conflict="update",
        )
        .execute_query()
    )

    assert transport.calls == 1  # nothing changed -> no update queued
    assert field.properties.get("Required") is True


def test_ensure_reconciles_type_and_description():
    ctx, transport = _sp([_existing(Title="Notes", FieldTypeKind=2, Description="old"), {}])

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Notes", FieldTypeKind=FieldType.Note, Description="new"),
            on_conflict="update",
        )
        .execute_query()
    )

    assert transport.calls == 2  # noqa: PLR2004
    assert field.field_type_kind == FieldType.Note
    assert field.properties.get("Description") == "new"


def test_ensure_update_is_a_noop_when_already_reconciled():
    ctx, transport = _sp([_existing(Title="Status", FieldTypeKind=6, Choices={"results": ["A", "B"]})])

    ctx.web.lists.get_by_title("Tasks").fields.ensure(
        FieldCreationInformation(Title="Status", FieldTypeKind=FieldType.Choice, Choices=["A", "B"]),
        on_conflict="update",
    ).execute_query()

    assert transport.calls == 1


# --- create path -------------------------------------------------------------


def test_ensure_creates_rich_field_when_missing():
    ctx, transport = _sp(
        [
            _NOT_FOUND,
            _existing(Title="Status", InternalName="Status", FieldTypeKind=6, Choices={"results": ["A", "C"]}),
        ]
    )

    field = (
        ctx.web.lists.get_by_title("Tasks")
        .fields.ensure(
            FieldCreationInformation(Title="Status", FieldTypeKind=FieldType.Choice, Choices=["A", "C"]),
        )
        .execute_query()
    )

    assert transport.calls == 2  # noqa: PLR2004
    assert transport.requests[-1].url.endswith("Fields/AddField")
    assert field.internal_name == "Status"
    assert list(field.choices) == ["A", "C"]


# --- schema-XML create path (migration fidelity) -----------------------------


_SCHEMA = (
    '<Field ID="{id}" Name="ProjectType" StaticName="ProjectType" '
    'DisplayName="Project Type" Type="Choice" Format="Dropdown">'
    "<CHOICES><CHOICE>Internal</CHOICE><CHOICE>External</CHOICE></CHOICES></Field>"
)


def test_ensure_xml_creates_when_missing():
    ctx, transport = _sp(
        [
            _NOT_FOUND,
            _existing(Title="Project Type", InternalName="ProjectType", FieldTypeKind=6),
        ]
    )

    field = ctx.web.lists.get_by_title("Tasks").fields.ensure_xml(_SCHEMA, "ProjectType").execute_query()

    assert transport.calls == 2  # noqa: PLR2004
    assert "getByInternalNameOrTitle('ProjectType')" in transport.requests[0].url
    assert transport.requests[-1].url.endswith("Fields/CreateFieldAsXml")
    assert field.internal_name == "ProjectType"


def test_ensure_xml_keeps_existing_column():
    ctx, transport = _sp([_existing(Title="Project Type", InternalName="ProjectType", FieldTypeKind=6)])

    field = ctx.web.lists.get_by_title("Tasks").fields.ensure_xml(_SCHEMA, "ProjectType").execute_query()

    assert transport.calls == 1  # looked up only, nothing created
    assert field.internal_name == "ProjectType"


# --- schema copy -------------------------------------------------------------


def test_schema_xml_for_copy_strips_origin_specific_attributes():
    ctx, _ = _sp([])
    field = Field(ctx)
    field.set_property(
        "SchemaXml",
        '<Field SourceID="{src}" Version="2" ID="{id}" Name="X" StaticName="X" />',
    )

    xml = field.schema_xml_for_copy()

    assert xml is not None
    assert "SourceID" not in xml
    assert "Version" not in xml
    assert 'ID="{id}"' in xml
    assert 'Name="X"' in xml


def test_schema_xml_for_copy_returns_none_when_unloaded():
    ctx, _ = _sp([])
    assert Field(ctx).schema_xml_for_copy() is None
