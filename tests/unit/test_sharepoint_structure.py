"""Tests for the SharePoint list-structure capture snapshot."""

import json
import unittest

from office365.migration.sharepoint.structure import (
    ListStructure,
    WebScopeStructure,
    capture_list_structure,
    compare_web_scope_structure,
    web_scope_note,
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
        sealed=False,
        custom_formatter=None,
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
        self.sealed = sealed
        self.properties = {"CustomFormatter": custom_formatter}

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

    def select(self, props):
        return self

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
        custom_formatter=None,
    ):
        self.title = title
        self.view_type = view_type
        self.row_limit = row_limit
        self.paged = paged
        self.hidden = hidden
        self.default_view = default_view
        self.personal_view = personal_view
        self.properties = {"CustomFormatter": custom_formatter}
        self.view_query = view_query
        self.view_fields = _ViewFields(fields)


class _Views:
    def __init__(self, views):
        self._views = list(views)

    def get(self):
        return self

    def execute_query(self):
        return self._views


_DEFAULT_SETTINGS = {
    "EnableVersioning": True,
    "MajorVersionLimit": 50,
    "EnableModeration": False,
    "DraftVersionVisibility": 0,
    "EnableAttachments": True,
    "ReadSecurity": 1,
    "WriteSecurity": 1,
    "ValidationFormula": "",
    "ValidationMessage": "",
    "EnableMinorVersions": False,
    "MajorWithMinorVersionsLimit": 0,
}


class _List:
    def __init__(
        self,
        *,
        title="Tasks",
        base_template=100,
        base_type=0,
        description="A list",
        content_types_enabled=True,
        settings=None,
        fields=(),
        content_types=(),
        views=(),
    ):
        self.title = title
        self.base_template = base_template
        self.base_type = base_type
        self.description = description
        self.content_types_enabled = content_types_enabled
        self.properties = dict(_DEFAULT_SETTINGS if settings is None else settings)
        self.fields = _Fields(fields)
        self.content_types = _ContentTypes(content_types)
        self.views = _Views(views)
        self.ensured = None

    def ensure_properties(self, names):
        self.ensured = [*(self.ensured or []), *names]
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


class TestCaptureListSettings(unittest.TestCase):
    def test_captures_container_settings(self):
        lst = _List(
            settings={
                "EnableVersioning": True,
                "MajorVersionLimit": 12,
                "EnableModeration": True,
                "DraftVersionVisibility": 2,
                "EnableAttachments": False,
                "ReadSecurity": 2,
                "WriteSecurity": 2,
                "ValidationFormula": '=IF([Title]="",TRUE,FALSE)',
                "ValidationMessage": "Title is required",
            }
        )

        structure = capture_list_structure(lst)

        self.assertEqual(structure.settings["MajorVersionLimit"], 12)
        self.assertTrue(structure.settings["EnableModeration"])
        self.assertFalse(structure.settings["EnableAttachments"])
        self.assertEqual(structure.settings["ReadSecurity"], 2)
        self.assertEqual(structure.settings["ValidationMessage"], "Title is required")

    def test_does_not_capture_library_only_settings_on_a_list(self):
        lst = _List(
            base_type=0,
            settings={"EnableMinorVersions": True, "MajorWithMinorVersionsLimit": 7, "ForceCheckout": True},
        )

        structure = capture_list_structure(lst)

        self.assertEqual(structure.settings, {})

    def test_captures_library_only_settings_on_a_document_library(self):
        lst = _List(
            base_type=1,
            settings={
                "EnableVersioning": True,
                "EnableMinorVersions": True,
                "MajorWithMinorVersionsLimit": 7,
                "ForceCheckout": True,
            },
        )

        structure = capture_list_structure(lst)

        self.assertTrue(structure.settings["EnableMinorVersions"])
        self.assertEqual(structure.settings["MajorWithMinorVersionsLimit"], 7)
        self.assertTrue(structure.settings["ForceCheckout"])

    def test_skips_settings_the_list_does_not_report(self):
        lst = _List(settings={"EnableVersioning": True})

        structure = capture_list_structure(lst)

        self.assertEqual(structure.settings, {"EnableVersioning": True})

    def test_requests_every_setting_explicitly(self):
        lst = _List()

        capture_list_structure(lst)

        for name in ("EnableVersioning", "EnableModeration", "ValidationFormula"):
            self.assertIn(name, lst.ensured)


class TestFormattingCapture(unittest.TestCase):
    def test_column_and_view_formatting_are_captured(self):
        lst = _List(
            fields=[_Field("Status", schema='<Field Name="Status"/>', custom_formatter='{"elmType": "div"}')],
            views=[_View("All Items", custom_formatter='{"additionalRowClass": "x"}')],
        )

        structure = capture_list_structure(lst)

        self.assertEqual(structure.fields[0].custom_formatter, '{"elmType": "div"}')
        self.assertEqual(structure.views[0].custom_formatter, '{"additionalRowClass": "x"}')

    def test_an_spfx_field_customizer_is_not_mistaken_for_formatting(self):
        field = _Field("Tags", schema='<Field Name="Tags"/>')
        field.properties["ClientSideComponentId"] = "4a4b1f52-7f0e-4a2a-9d1f-2f0e4a2a9d1f"

        structure = capture_list_structure(_List(fields=[field]))

        self.assertEqual(structure.fields[0].client_side_component_id, "4a4b1f52-7f0e-4a2a-9d1f-2f0e4a2a9d1f")
        self.assertIsNone(structure.fields[0].custom_formatter)

    def test_an_unset_component_id_is_reported_as_absent(self):
        field = _Field("Tags", schema='<Field Name="Tags"/>')
        field.properties["ClientSideComponentId"] = "00000000-0000-0000-0000-000000000000"

        structure = capture_list_structure(_List(fields=[field]))

        self.assertIsNone(structure.fields[0].client_side_component_id)


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


class _Web:
    """A web as the web-scope comparison sees it (two projected collections)."""

    def __init__(self, fields=(), content_types=()):
        self.fields = _Fields(fields)
        self.content_types = _ContentTypes(content_types)


class TestCompareWebScopeStructure(unittest.TestCase):
    """A per-list replay leaves web-scope definitions behind; the helpers name them."""

    def test_reports_the_columns_and_content_types_the_target_lacks(self):
        source = _Web(
            fields=[_Field("Region"), _Field("Cost Centre")],
            content_types=[_ContentType("0x0100ABCDEF0123456789ABCDEF0123456789", name="Contract")],
        )
        target = _Web(fields=[_Field("Region")])

        missing = compare_web_scope_structure(source, target)

        self.assertEqual(missing.columns, ["Cost Centre"])
        self.assertEqual(missing.content_types, ["Contract"])
        self.assertFalse(missing.is_empty)

    def test_matches_columns_by_internal_name_and_content_types_by_name(self):
        # A content type's string_id is assigned by the server, so the same type on
        # the target carries a different one — it must still count as present.
        source = _Web(content_types=[_ContentType("0x0100AAAA", name="Contract")])
        target = _Web(content_types=[_ContentType("0x0100BBBB", name="contract")])

        missing = compare_web_scope_structure(source, target)

        self.assertTrue(missing.is_empty)

    def test_skips_hidden_framework_sealed_and_protected_columns(self):
        source = _Web(
            fields=[
                _Field("Hidden", hidden=True),
                _Field("Framework", from_base_type=True),
                _Field("SealedColumn", sealed=True),
                _Field("Protected", can_be_deleted=False),
                _Field("FileRef"),
                _Field("UserColumn"),
            ]
        )

        missing = compare_web_scope_structure(source, _Web())

        self.assertEqual(missing.columns, ["UserColumn"])

    def test_skips_hidden_content_types(self):
        source = _Web(content_types=[_ContentType("0x0100AA", name="Internal", hidden=True)])

        missing = compare_web_scope_structure(source, _Web())

        self.assertEqual(missing.content_types, [])

    def test_note_names_a_sample_and_counts_the_rest(self):
        missing = WebScopeStructure(columns=["A", "B", "C", "D", "E", "F", "G"])

        note = web_scope_note(missing, "https://contoso.sharepoint.com/sites/target")

        self.assertIsNotNone(note)
        self.assertIn("7 column(s): A, B, C, D, E (+2 more)", note)
        self.assertIn("the target of https://contoso.sharepoint.com/sites/target", note)
        self.assertIn("list-scoped copy", note)

    def test_note_is_none_when_the_target_has_every_definition(self):
        self.assertIsNone(web_scope_note(compare_web_scope_structure(_Web(), _Web())))


if __name__ == "__main__":
    unittest.main()
