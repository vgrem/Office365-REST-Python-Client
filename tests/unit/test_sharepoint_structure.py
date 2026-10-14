"""Tests for the SharePoint list-structure capture snapshot."""

import json
import unittest

from office365.migration.sharepoint.structure import (
    ListStructure,
    capture_list_structure,
)
from office365.sharepoint.fields.type import FieldType


class _Field:
    def __init__(
        self,
        internal_name,
        *,
        title=None,
        kind=None,
        schema=None,
        required=None,
        hidden=False,
        read_only=False,
        from_base_type=None,
        can_be_deleted=None,
        group=None,
        description=None,
        type_as_string=None,
    ):
        self.internal_name = internal_name
        self.title = title
        self.field_type_kind = kind
        self._schema = schema
        self.required = required
        self.hidden = hidden
        self.read_only_field = read_only
        self.from_base_type = from_base_type
        self.can_be_deleted = can_be_deleted
        self.group = group
        self.description = description
        self.type_as_string = type_as_string

    def schema_xml_for_copy(self):
        if self._schema is None:
            return None
        return self._schema.replace(' SourceID="origin"', "").replace(' Version="1"', "")


class _Fields:
    def __init__(self, fields):
        self._fields = list(fields)
        self.selected = None

    def select(self, props):
        self.selected = list(props)
        return self

    def get(self):
        return self

    def execute_query(self):
        return self._fields


class _FieldLink:
    def __init__(self, name):
        self.field_internal_name = name


class _FieldLinks:
    def __init__(self, names):
        self._links = [_FieldLink(name) for name in names]

    def get(self):
        return self

    def execute_query(self):
        return self._links


class _ContentType:
    def __init__(
        self,
        string_id,
        *,
        name=None,
        group=None,
        description=None,
        hidden=False,
        sealed=False,
        read_only=False,
        links=(),
    ):
        self.string_id = string_id
        self.name = name
        self.group = group
        self.description = description
        self.hidden = hidden
        self.sealed = sealed
        self.read_only = read_only
        self.field_links = _FieldLinks(links)


class _ContentTypes:
    def __init__(self, content_types):
        self._content_types = list(content_types)

    def get(self):
        return self

    def execute_query(self):
        return self._content_types


class _ViewFields:
    def __init__(self, names):
        self._names = list(names)

    def get(self):
        return self

    def execute_query(self):
        return self._names


class _View:
    def __init__(
        self,
        title,
        *,
        view_type=None,
        row_limit=None,
        paged=None,
        hidden=False,
        default_view=False,
        personal_view=False,
        view_query=None,
        fields=(),
    ):
        self.title = title
        self.view_type = view_type
        self.row_limit = row_limit
        self.paged = paged
        self.hidden = hidden
        self.default_view = default_view
        self.personal_view = personal_view
        self.view_query = view_query
        self.view_fields = _ViewFields(fields)


class _Views:
    def __init__(self, views):
        self._views = list(views)

    def get(self):
        return self

    def execute_query(self):
        return self._views


class _List:
    def __init__(
        self,
        *,
        title="Tasks",
        base_template=100,
        base_type=0,
        description="A list",
        content_types_enabled=True,
        fields=(),
        content_types=(),
        views=(),
    ):
        self.title = title
        self.base_template = base_template
        self.base_type = base_type
        self.description = description
        self.content_types_enabled = content_types_enabled
        self.fields = _Fields(fields)
        self.content_types = _ContentTypes(content_types)
        self.views = _Views(views)
        self.ensured = None

    def ensure_properties(self, names):
        self.ensured = list(names)
        return self

    def execute_query(self):
        return self


class TestCaptureListStructure(unittest.TestCase):
    def test_captures_metadata_and_columns(self):
        lst = _List(
            fields=[
                _Field("_ModerationStatus"),
                _Field(
                    "ProjectType",
                    title="Project Type",
                    kind=FieldType.Choice,
                    type_as_string="Choice",
                    schema='<Field Type="Choice" Name="ProjectType" SourceID="origin" Version="1"/>',
                    required=True,
                    group="Custom Columns",
                    description="Kind of project",
                ),
            ]
        )

        structure = capture_list_structure(lst)

        self.assertEqual(structure.title, "Tasks")
        self.assertEqual(structure.base_template, 100)
        self.assertEqual(structure.base_type, 0)
        self.assertTrue(structure.content_types_enabled)
        self.assertEqual([f.internal_name for f in structure.fields], ["ProjectType"])
        project = structure.fields[0]
        self.assertEqual(project.field_type_kind, FieldType.Choice.value)
        self.assertEqual(project.type_as_string, "Choice")
        self.assertEqual(project.required, True)
        self.assertEqual(project.group, "Custom Columns")
        self.assertNotIn("SourceID", project.schema_xml)
        self.assertNotIn("Version", project.schema_xml)

    def test_skips_builtin_framework_and_hidden_columns(self):
        lst = _List(
            fields=[
                _Field("_ModerationStatus"),
                _Field("BuiltIn", from_base_type=True),
                _Field("Framework", from_base_type=False, can_be_deleted=False),
                _Field("HiddenUser", from_base_type=False, can_be_deleted=True, hidden=True),
                _Field("RealUser", from_base_type=False, can_be_deleted=True),
            ]
        )

        structure = capture_list_structure(lst)

        self.assertEqual([f.internal_name for f in structure.fields], ["RealUser"])

    def test_requests_schema_xml_for_each_column(self):
        lst = _List(fields=[_Field("Tags")])

        capture_list_structure(lst)

        self.assertIn("SchemaXml", lst.fields.selected)

    def test_loads_list_properties_before_capturing(self):
        lst = _List()

        capture_list_structure(lst)

        self.assertIn("BaseTemplate", lst.ensured)
        self.assertIn("ContentTypesEnabled", lst.ensured)

    def test_captures_content_types_and_skips_hidden(self):
        lst = _List(
            content_types=[
                _ContentType("0x0100abc", name="Project", group="Custom", links=["Title", "ProjectType"]),
                _ContentType("0x01", name="Item", hidden=True, links=["Title"]),
            ]
        )

        structure = capture_list_structure(lst)

        self.assertEqual([ct.name for ct in structure.content_types], ["Project"])
        project = structure.content_types[0]
        self.assertEqual(project.string_id, "0x0100abc")
        self.assertEqual(project.field_internal_names, ["Title", "ProjectType"])

    def test_captures_views_in_order_and_skips_hidden_and_personal(self):
        lst = _List(
            views=[
                _View(
                    "All Items",
                    view_type="HTML",
                    row_limit=30,
                    paged=True,
                    default_view=True,
                    fields=["Title", "ProjectType"],
                ),
                _View("Hidden", hidden=True, fields=["Title"]),
                _View("My View", personal_view=True, fields=["Title"]),
            ]
        )

        structure = capture_list_structure(lst)

        self.assertEqual([view.title for view in structure.views], ["All Items"])
        view = structure.views[0]
        self.assertEqual(view.view_type, "HTML")
        self.assertEqual(view.row_limit, 30)
        self.assertTrue(view.default_view)
        self.assertEqual(view.field_internal_names, ["Title", "ProjectType"])

    def test_document_library_flag(self):
        library = _List(title="Documents", base_template=101, base_type=1)

        structure = capture_list_structure(library)

        self.assertTrue(structure.is_document_library)


class TestListStructureSerialization(unittest.TestCase):
    def _capture(self):
        lst = _List(
            fields=[_Field("ProjectType", kind=FieldType.Text, schema='<Field Name="ProjectType" SourceID="origin"/>')],
            content_types=[_ContentType("0x0100abc", name="Project", links=["Title", "ProjectType"])],
            views=[_View("All Items", row_limit=30, fields=["Title"])],
        )
        return capture_list_structure(lst)

    def test_json_round_trip(self):
        structure = self._capture()

        restored = ListStructure.from_dict(json.loads(json.dumps(structure.to_dict())))

        self.assertEqual(restored, structure)
        self.assertEqual(restored.fields[0].schema_xml, structure.fields[0].schema_xml)

    def test_from_dict_tolerates_missing_and_unknown_keys(self):
        restored = ListStructure.from_dict({"title": "X", "unknown": 1})

        self.assertEqual(restored.title, "X")
        self.assertEqual(restored.fields, [])
        self.assertEqual(restored.content_types, [])
        self.assertEqual(restored.views, [])

    def test_empty_structure_round_trips(self):
        empty = ListStructure(title="Empty")

        self.assertEqual(ListStructure.from_dict(empty.to_dict()), empty)


if __name__ == "__main__":
    unittest.main()
