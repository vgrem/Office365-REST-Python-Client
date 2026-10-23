"""Offline tests for replaying a captured list structure onto a target list.

``provision_list_structure`` is imperative (it issues and executes requests), so
these tests script the request/response exchange with the shared method-aware
routing transport, which also expands ``$batch`` payloads into their
sub-requests. They assert both that the right endpoints are hit and that the
content-type field-link URLs are correctly pathed from the reloaded content type.
"""

from __future__ import annotations

from office365.migration.sharepoint.structure import (
    ContentTypeDefinition,
    FieldDefinition,
    ListStructure,
    ViewDefinition,
    provision_list_structure,
    rewrite_lookup_schema,
)
from office365.runtime.http.http_method import HttpMethod
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import MethodRoutingTransport, build_response

_CT_ID = "0x0100abcdefabcdefabcdefabcdefab"
# a field-link round is read, written and read back
_LINK_READS = 2
# the atomic-rollback case links two columns, and loses both
_LINKED_COLUMNS = 2

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}


_MethodRoutingTransport = MethodRoutingTransport


def _structure(**overrides):
    base = {
        "title": "Tasks",
        "base_template": 171,
        "base_type": 0,
        "content_types_enabled": True,
        "fields": [
            FieldDefinition(
                internal_name="ProjectType",
                title="Project Type",
                field_type_kind=6,
                schema_xml='<Field Name="ProjectType" StaticName="ProjectType" Type="Choice"/>',
            )
        ],
        "content_types": [
            ContentTypeDefinition(
                string_id=_CT_ID,
                name="Project",
                group="Custom",
                field_internal_names=["Title", "ProjectType"],
            )
        ],
        "views": [
            ViewDefinition(
                title="All Items",
                view_type="HTML",
                row_limit=30,
                field_internal_names=["Title", "ProjectType"],
            )
        ],
    }
    base.update(overrides)
    return ListStructure(**base)


def _routes():
    return [
        # phase 1 -----------------------------------------------------------------
        (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": False}}),
        (HttpMethod.Post, "GetByTitle('Tasks')", {}),  # MERGE list (enable content types)
        (HttpMethod.Get, "getByInternalNameOrTitle", _NOT_FOUND),
        (HttpMethod.Post, "CreateFieldAsXml", {"d": {"InternalName": "ProjectType", "FieldTypeKind": 6}}),
        # field links must be matched before the bare /ContentTypes POST/GET ------
        (HttpMethod.Post, "/FieldLinks/Reorder", {}),
        (HttpMethod.Post, "/FieldLinks", {}),
        (HttpMethod.Get, "/FieldLinks", {"d": {"results": []}}),
        # get-first content type: the filtered lookup misses, then the create runs
        (HttpMethod.Get, "ContentTypes?$filter=", {"d": {"results": []}}),
        (HttpMethod.Post, "/ContentTypes", {"d": {"Name": "Project", "StringId": _CT_ID}}),
        (
            HttpMethod.Get,
            "/ContentTypes",
            {"d": {"results": [{"Name": "Project", "StringId": _CT_ID, "Group": "Custom"}]}},
        ),
        # phase 2 -----------------------------------------------------------------
        (
            HttpMethod.Get,
            "Fields?$select=InternalName",
            {"d": {"results": [{"InternalName": "Title"}, {"InternalName": "ProjectType"}]}},
        ),
        (HttpMethod.Get, "views/GetByTitle", _NOT_FOUND),
        (HttpMethod.Post, "views/Add", {"d": {"Title": "All Items"}}),
    ]


class _OfflineAuth:
    """Stand-in authentication context: nothing is signed, offline."""

    url = test_site_url
    is_configured = False
    is_async_token_callback = False

    def authenticate_request(self, request):
        return None


def _setup(routes, transport=None):
    ctx = ClientContext(test_site_url)
    request = ctx.pending_request()
    request.beforeExecute.clear()
    # ``execute_batch`` re-registers auth and the form digest on the batch request
    # itself, so an offline run needs a digest and an auth context that signs nothing.
    request._auth_context = _OfflineAuth()  # noqa: SLF001 - offline, no credentials
    request.context_info.FormDigestValue = "offline-digest"
    transport = transport if transport is not None else _MethodRoutingTransport(routes)
    request.transport = transport
    return ctx, transport


def _urls(transport):
    return [request.url for request in transport.requests]


def _posts(transport):
    return [request for request in transport.requests if request.method == HttpMethod.Post]


def test_provision_creates_columns_content_type_links_and_view():
    ctx, transport = _setup(_routes())
    sp_list = ctx.web.lists.get_by_title("Tasks")

    provision_list_structure(sp_list, _structure())

    urls = _urls(transport)
    assert any(u.endswith("Fields/getByInternalNameOrTitle('ProjectType')") for u in urls)
    assert any(u.endswith("Fields/CreateFieldAsXml") for u in urls)
    assert any(p.url.endswith("/ContentTypes") for p in _posts(transport))
    # field links are pathed through the reloaded content type id, not the collection
    assert any(u.endswith("/ContentTypes('" + _CT_ID + "')/FieldLinks") for u in urls)
    assert sum(1 for p in _posts(transport) if p.url.endswith("/FieldLinks")) == 1  # only the captured column
    # the links are read back afterwards: a change set is atomic, so a refused
    # column rolls its siblings back while their sub-responses still say 200
    reads = [r for r in transport.requests if r.method == HttpMethod.Get and r.url.endswith("/FieldLinks")]
    assert len(reads) == _LINK_READS
    assert any(u.endswith("views/GetByTitle('All Items')") for u in urls)
    assert any(u.endswith("views/Add") for u in urls)


# --- content type creation information (regression: Group landed in Id) -------


_LINK_REJECTED = {
    "http_status": 400,
    "body": {
        "error": {
            "code": "-2147024809, System.ArgumentException",
            "message": {"lang": "en-US", "value": "Column 'ProjectType' does not exist."},
        }
    },
}


# --- lookup columns: repoint the schema at the target list --------------------

_SOURCE_LIST_ID = "a6879990-804b-4064-bf5d-f0c5c65ef768"
_TARGET_LIST_ID = "ed0abd71-7d64-429a-9de7-7dfabbac6aa7"
_LOOKUP_SCHEMA = (
    '<Field Type="Lookup" List="{A6879990-804B-4064-BF5D-F0C5C65EF768}" '
    'ShowField="Title" StaticName="Dept" Name="Dept"/>'
)


def test_rewrite_lookup_schema_repoints_list_attribute():
    rewritten, unresolved = rewrite_lookup_schema(_LOOKUP_SCHEMA, {_SOURCE_LIST_ID: _TARGET_LIST_ID})

    assert unresolved is None
    assert 'List="{ed0abd71-7d64-429a-9de7-7dfabbac6aa7}"' in rewritten
    assert "A6879990" not in rewritten


def test_provision_skips_an_external_data_column():
    """A BCS column references a BDC model: replaying its schema creates a dead column."""
    ctx, transport = _setup(
        [
            (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        ]
    )
    structure = _structure(
        fields=[
            FieldDefinition(
                internal_name="CustomerName",
                title="Customer",
                field_type_kind=10,
                type_as_string="BusinessData",
                schema_xml='<Field Type="BusinessData" Name="CustomerName" StaticName="CustomerName"/>',
            )
        ],
        content_types=[],
        views=[],
    )

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert len(warnings) == 1
    assert "CustomerName" in warnings[0]
    assert "external (BCS) content type" in warnings[0]
    assert not any(p.url.endswith("Fields/CreateFieldAsXml") for p in _posts(transport))


# ── Managed Metadata (taxonomy) columns ──────────────────────────────────────

_TAXONOMY_SCHEMA = (
    '<Field Type="TaxonomyFieldType" DisplayName="Dept" Name="Dept" StaticName="Dept" '
    'Mult="FALSE" WebId="{11111111-1111-1111-1111-111111111111}">'
    "<Default></Default>"
    "<Customization><ArrayOfProperty>"
    "<Property><Name>SspId</Name>"
    '<Value xmlns:q1="http://www.w3.org/2001/XMLSchema" p4:type="q1:string" '
    'xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">f02be691-d551-462f-aaae-e1c89168cd0b</Value></Property>'
    "<Property><Name>TermSetId</Name>"
    '<Value xmlns:q1="http://www.w3.org/2001/XMLSchema" p4:type="q1:string" '
    'xmlns:p4="http://www.w3.org/2001/XMLSchema-instance">a83fe90d-4bdb-4644-a484-7f75ee3f5730</Value></Property>'
    "</ArrayOfProperty></Customization>"
    "</Field>"
)

_NOTE_ID = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
_WEB_ID = "ef40c956-7276-421a-b0a4-d81ccf839bd9"


# --- container settings (versioning, moderation, item-level policy, ...) -------


class _RejectingSettingTransport(_MethodRoutingTransport):
    """Rejects the one MERGE that carries ``rejected``; every other route succeeds."""

    def __init__(self, routes, rejected):
        super().__init__(routes)
        self._rejected = rejected

    def dispatch(self, request):
        if isinstance(request.data, dict) and self._rejected in request.data:
            self.requests.append(request)
            return build_response(
                request,
                {
                    "http_status": 400,
                    "body": {
                        "error": {
                            "code": "-2146232832, Microsoft.SharePoint.SPException",
                            "message": {"value": "The list does not support minor versioning."},
                        }
                    },
                },
            )
        return super().dispatch(request)


def _empty_structure(**overrides):
    base = {
        "title": "Tasks",
        "base_template": 100,
        "base_type": 0,
        "content_types_enabled": None,
        "fields": [],
        "content_types": [],
        "views": [],
    }
    base.update(overrides)
    return ListStructure(**base)


def _merges(transport):
    return [p for p in _posts(transport) if p.headers.get("X-HTTP-Method") == "MERGE"]


def _settings_written(transport):
    """The setting each MERGE carried, without the OData type annotation."""
    return [{k: v for k, v in p.data.items() if k != "__metadata"} for p in _merges(transport)]


def _setting_routes(current=None):
    """A GET reporting the target's current settings, then the per-setting MERGEs."""
    return [
        (HttpMethod.Get, "GetByTitle('Tasks')", {"d": current or {}}),
        (HttpMethod.Post, "GetByTitle('Tasks')", {}),
    ]


def test_provision_applies_each_container_setting_by_title():
    ctx, transport = _setup(_setting_routes())
    structure = _empty_structure(settings={"EnableVersioning": True, "MajorVersionLimit": 12})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert _settings_written(transport) == [{"EnableVersioning": True}, {"MajorVersionLimit": 12}]
    assert all(m.url.endswith("lists/GetByTitle('Tasks')") for m in _merges(transport))


def test_provision_reports_a_rejected_setting_as_a_warning():
    routes = _setting_routes()
    ctx, transport = _setup(routes, _RejectingSettingTransport(routes, "EnableMinorVersions"))
    structure = _empty_structure(base_type=1, settings={"EnableMinorVersions": True, "ForceCheckout": True})

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert len(warnings) == 1
    assert "EnableMinorVersions" in warnings[0]
    # the rejected setting does not stop the ones after it
    assert {"ForceCheckout": True} in _settings_written(transport)


_COLUMN_FORMATTER = '{"$schema": "column", "elmType": "div"}'
_VIEW_FORMATTER = '{"additionalRowClass": "sp-field-severity--good"}'


def _formatting_structure(*, column_formatter=_COLUMN_FORMATTER, view_formatter=_VIEW_FORMATTER):
    """A snapshot whose columns/views already exist on the target: only formatting is left."""
    return ListStructure(
        title="Tasks",
        base_template=171,
        base_type=0,
        fields=[FieldDefinition(internal_name="Status", custom_formatter=column_formatter)],
        views=[ViewDefinition(title="All Items", custom_formatter=view_formatter)],
    )


def _formatting_routes(*, field_read_back=None, view_read_back=None):
    """Routes for the formatting pass: read both sides, MERGE the differing ones, read back."""
    return [
        (HttpMethod.Get, "Fields/getByInternalNameOrTitle('Status')", {"d": {"InternalName": "Status"}}),
        (HttpMethod.Post, "Fields/getByInternalNameOrTitle('Status')", {}),
        (HttpMethod.Get, "views/GetByTitle('All Items')", {"d": {"Title": "All Items"}}),
        (HttpMethod.Post, "views/GetByTitle('All Items')", {}),
        (
            HttpMethod.Get,
            "Fields?$select=InternalName,CustomFormatter",
            {"d": {"results": [{"InternalName": "Status", "CustomFormatter": field_read_back}]}},
        ),
        # the column-name read for the view replay: after the formatter read-back,
        # whose key is a superstring of it
        (HttpMethod.Get, "Fields?$select=InternalName", {"d": {"results": [{"InternalName": "Status"}]}}),
        (
            HttpMethod.Get,
            "views",
            {"d": {"results": [{"Title": "All Items", "CustomFormatter": view_read_back}]}},
        ),
    ]


def test_provision_writes_column_and_view_formatting():
    ctx, transport = _setup(_formatting_routes(field_read_back=_COLUMN_FORMATTER, view_read_back=_VIEW_FORMATTER))

    warnings = provision_list_structure(
        ctx.web.lists.get_by_title("Tasks"),
        _formatting_structure(),
    )

    merges = [p for p in _posts(transport) if p.headers.get("X-HTTP-Method") == "MERGE"]
    assert any("Fields/getByInternalNameOrTitle('Status')" in p.url for p in merges)
    assert any("views/GetByTitle('All Items')" in p.url for p in merges)
    assert warnings == []


def test_provision_reports_an_spfx_field_customizer_instead_of_copying_it():
    ctx, transport = _setup([])
    component_id = "4a4b1f52-7f0e-4a2a-9d1f-2f0e4a2a9d1f"

    warnings = provision_list_structure(
        ctx.web.lists.get_by_title("Tasks"),
        ListStructure(
            title="Tasks",
            base_template=171,
            base_type=0,
            fields=[FieldDefinition(internal_name="Tags", client_side_component_id=component_id)],
        ),
    )

    assert warnings == [
        f"column 'Tags' carries an SPFx field customizer ({component_id}), which is not carried: "
        "the solution has to be deployed on the target"
    ]
    assert _urls(transport) == []
