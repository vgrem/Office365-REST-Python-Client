"""Offline tests for Managed Metadata (taxonomy) field handling.

Covers the base-library fixes that make a taxonomy column usable: the field is
created without a ``List`` attribute (so its ``LookupList`` binds to the web's
hidden TaxonomyHiddenList), a multi-value collection is actually populated, and
a multi-value write lands on the hidden note companion column.
"""

from __future__ import annotations

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.taxonomy.create_xml_parameters import TaxonomyFieldCreateXmlParameters
from office365.sharepoint.taxonomy.field_value import TaxonomyFieldValue
from office365.sharepoint.taxonomy.field_value_col import TaxonomyFieldValueCollection
from tests import test_site_url
from tests._scripted_transport import ScriptedTransport


def _ctx(payloads):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = ScriptedTransport(payloads)
    return ctx


def test_taxonomy_schema_omits_list_attribute():
    params = TaxonomyFieldCreateXmlParameters(
        Name="Dept",
        SspId="f02be691-d551-462f-aaae-e1c89168cd0b",
        TermSetId="4d7c4109-db97-4c49-8f7f-a72f0785ee3c",
        FieldId="11111111-1111-1111-1111-111111111111",
        WebId="22222222-2222-2222-2222-222222222222",
        TextFieldId="33333333-3333-3333-3333-333333333333",
    )
    schema = params.schema_xml
    assert 'Type="TaxonomyFieldType"' in schema
    assert "List=" not in schema
    assert 'WebId="22222222-2222-2222-2222-222222222222"' in schema
    assert "4d7c4109-db97-4c49-8f7f-a72f0785ee3c" in schema


def test_set_taxonomy_collection_writes_note_companion():
    note_id = "33333333-3333-3333-3333-333333333333"
    # The companion name is resolved synchronously (a deferred lookup would run
    # after the write payload was built): the taxonomy column's TextField id, then
    # the hidden note field, whose *item* property is its EntityPropertyName.
    ctx = _ctx(
        [
            {"d": {"TextField": note_id}},
            {"d": {"EntityPropertyName": "Dept_0"}},
        ]
    )
    lst = ctx.web.lists.get_by_title("Tasks")
    item = ListItem(ctx, None, lst)
    item.set_property("Dept", TaxonomyFieldValueCollection([TaxonomyFieldValue(Label="TermA", TermGuid="a" * 8)]))
    assert item.properties.get("Dept_0") == "-1;#TermA|aaaaaaaa"


def test_set_taxonomy_collection_missing_companion_is_ignored():
    ctx = _ctx(
        [
            {
                "http_status": 404,
                "body": {"error": {"code": "System.ArgumentException", "message": "Column does not exist."}},
            }
        ]
    )
    lst = ctx.web.lists.get_by_title("Tasks")
    item = ListItem(ctx, None, lst)
    item.set_property("Dept", TaxonomyFieldValueCollection([TaxonomyFieldValue(Label="TermA", TermGuid="a" * 8)]))
    assert "Dept_0" not in item.properties
