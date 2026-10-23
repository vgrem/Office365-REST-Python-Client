"""Web-scope column provisioning: what lands on the target web, and what is reported."""

import re

from office365.migration.sharepoint.structure import (
    WebScopeProvisionReport,
    provision_web_scope_columns,
)

TEXT_SCHEMA = '<Field Type="Text" DisplayName="Region" Name="{name}" StaticName="{name}" ID="{{new}}" />'
TAXONOMY_SCHEMA = """
<Field Type="TaxonomyFieldType" DisplayName="Region" Name="{name}" StaticName="{name}">
  <Customization>
    <ArrayOfProperty>
      <Property>
        <Name>TermSetId</Name>
        <Value xmlns:q6="http://schemas.datacontract.org/2004/07/System" p4:type="q6:string"
          xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">a83fe90d-4bdb-4644-a484-7f75ee3f5730</Value>
      </Property>
    </ArrayOfProperty>
  </Customization>
</Field>
"""


class _Field:
    """A web field as the web-scope comparison and provisioning see it."""

    def __init__(
        self,
        internal_name,
        type_as_string="Text",
        schema_xml=None,
        hidden=False,
        from_base_type=False,
        can_be_deleted=True,
        sealed=False,
    ):
        self.internal_name = internal_name
        self.title = internal_name
        self.type_as_string = type_as_string
        self.field_type_kind = 2
        self.schema_xml = schema_xml
        self.hidden = hidden
        self.from_base_type = from_base_type
        self.can_be_deleted = can_be_deleted
        self.sealed = sealed
        self.required = False
        self.read_only_field = False
        self.group = None
        self.description = None
        self.properties = {}

    def schema_xml_for_copy(self):
        """The real :meth:`Field.schema_xml_for_copy` drops the origin attributes."""
        if self.schema_xml is None:
            return None
        return re.sub(r'\s*(?:SourceID|Version)="[^"]*"', "", self.schema_xml)


class _Query:
    """A deferred create: it only does something when executed."""

    def __init__(self, action):
        self._action = action

    def execute_query(self):
        return self._action()


class _FieldView:
    """``get_by_internal_name_or_title(name).get()`` over a live field list."""

    def __init__(self, fields, name):
        self._fields = fields
        self._name = name

    def get(self):
        return self

    def execute_query(self):
        for field in self._fields:
            if field.internal_name == self._name:
                return field
        raise RuntimeError(f"Column '{self._name}' does not exist.")


class _Fields:
    """A web's ``fields`` collection: projectable, gettable, creatable."""

    def __init__(self, fields=None, on_create=None):
        self.entries = list(fields or [])
        self.created: list[str] = []
        self.on_create = on_create
        self.context = None

    def select(self, names):
        return self

    def get(self):
        return self

    def execute_query(self):
        return list(self.entries)

    def get_by_internal_name_or_title(self, name):
        return _FieldView(self.entries, name)

    def create_field_as_xml(self, schema_xml, return_type=None):
        def _create():
            self.created.append(schema_xml)
            if self.on_create is not None:
                return self.on_create(self, schema_xml)
            self.entries.append(_Field(_schema_name(schema_xml), schema_xml=schema_xml))
            return None

        return _Query(_create)


def _schema_name(schema_xml):
    marker = 'Name="'
    start = schema_xml.index(marker) + len(marker)
    return schema_xml[start : schema_xml.index('"', start)]


class _Web:
    def __init__(self, fields=None, content_types=None):
        self.fields = _Fields(fields)
        self.content_types = _ContentTypes(content_types or [])


class _ContentTypes:
    def __init__(self, entries):
        self._entries = list(entries)

    def select(self, names):
        return self

    def get(self):
        return self

    def execute_query(self):
        return list(self._entries)


def _web(name="Region", schema_xml=None, **kwargs):
    """A source web carrying one web-scope column."""
    schema = (TEXT_SCHEMA if schema_xml is None else schema_xml).format(name=name, **kwargs)
    return _Web([_Field(name, schema_xml=schema)])


def test_run_is_idempotent():
    source, target = _web(), _Web()

    first = provision_web_scope_columns(source, target)
    second = provision_web_scope_columns(source, target)

    assert first.created == ["Region"]
    assert second.present == ["Region"]
    assert target.fields.created == [source.fields.entries[0].schema_xml]


def test_lookup_is_repointed_at_the_target_list():
    schema = (
        '<Field Type="Lookup" DisplayName="Region" Name="Region" StaticName="Region" '
        'List="{11111111-1111-1111-1111-111111111111}" ShowField="Title" />'
    )
    source = _Web([_Field("Region", type_as_string="Lookup", schema_xml=schema)])
    target = _Web()

    report = provision_web_scope_columns(
        source, target, list_id_map={"11111111-1111-1111-1111-111111111111": "22222222-2222-2222-2222-222222222222"}
    )

    assert report.created == ["Region"]
    assert "22222222-2222-2222-2222-222222222222" in target.fields.created[0]


def test_report_renders_what_it_did():
    report = WebScopeProvisionReport(created=["A"], present=["B", "C"], skipped=["note"], failed={"D": "boom"})

    assert report.summary() == "web-scope columns: 1 created, 2 already present, 1 skipped, 1 failed"
    assert report.to_dict() == {
        "created": ["A"],
        "present": ["B", "C"],
        "skipped": ["note"],
        "failed": {"D": "boom"},
    }
    assert not report.is_empty
