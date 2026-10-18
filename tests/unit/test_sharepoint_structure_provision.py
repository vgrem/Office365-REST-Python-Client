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
    normalize_guid,
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


def _setup(routes):
    ctx = ClientContext(test_site_url)
    request = ctx.pending_request()
    request.beforeExecute.clear()
    # ``execute_batch`` re-registers auth and the form digest on the batch request
    # itself, so an offline run needs a digest and an auth context that signs nothing.
    request._auth_context = _OfflineAuth()  # noqa: SLF001 - offline, no credentials
    request.context_info.FormDigestValue = "offline-digest"
    transport = _MethodRoutingTransport(routes)
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


def test_provision_enables_content_types_only_when_off():
    routes = _routes()
    routes[0] = (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}})
    ctx, transport = _setup(routes)

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure())

    merges = [p for p in _posts(transport) if p.headers.get("X-HTTP-Method") == "MERGE"]
    assert merges == []


def test_provision_skips_base_content_types():
    ctx, transport = _setup(
        [
            (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": False}}),
            (HttpMethod.Post, "GetByTitle('Tasks')", {}),
        ]
    )
    structure = _structure(
        fields=[],
        content_types=[ContentTypeDefinition(string_id="0x0101", name="Document", field_internal_names=["Title"])],
        views=[],
    )

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    urls = _urls(transport)
    assert not any("/FieldLinks" in u for u in urls)
    assert not any(p.url.endswith("/ContentTypes") for p in _posts(transport))


def test_provision_records_content_type_id_map_by_name():
    # SharePoint assigns a recreated list content type a fresh StringId; the
    # populated map (source id -> target id) lets item ContentTypeIds be rewritten.
    target_id = "0x0100ffffffffffffffffffffffff0001"
    routes = [
        (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        (HttpMethod.Get, "getByInternalNameOrTitle", _NOT_FOUND),
        (HttpMethod.Post, "CreateFieldAsXml", {"d": {"InternalName": "ProjectType", "FieldTypeKind": 6}}),
        (HttpMethod.Get, "/FieldLinks", {"d": {"results": []}}),
        (HttpMethod.Post, "/FieldLinks/Reorder", {}),
        (HttpMethod.Post, "/FieldLinks", {}),
        (HttpMethod.Get, "ContentTypes?$filter=", {"d": {"results": []}}),
        (HttpMethod.Post, "/ContentTypes", {"d": {"Name": "Project", "StringId": target_id}}),
        (HttpMethod.Get, "/ContentTypes", {"d": {"results": [{"Name": "Project", "StringId": target_id}]}}),
    ]
    ctx, _ = _setup(routes)

    mapping: dict = {}
    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure(views=[]), content_type_map=mapping)

    assert mapping == {_CT_ID: target_id}


def test_provision_omits_map_when_ids_are_unchanged():
    ctx, _ = _setup(_routes())

    mapping: dict = {}
    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure(), content_type_map=mapping)

    # the scripted target returns the same StringId as the source
    assert mapping == {}


def test_provision_rejects_unknown_conflict_mode():
    ctx, _ = _setup([])
    try:
        provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure(), on_conflict="merge")
    except ValueError as exc:
        assert "on_conflict" in str(exc)
    else:  # pragma: no cover - defensive
        raise AssertionError("expected ValueError")


# --- content type creation information (regression: Group landed in Id) -------


def test_ensure_content_type_sets_group_and_preserves_id():
    ctx, transport = _setup(
        [
            (HttpMethod.Get, "ContentTypes?$filter=", {"d": {"results": []}}),
            (HttpMethod.Post, "/ContentTypes", {"d": {"Name": "Project", "StringId": _CT_ID}}),
        ]
    )

    ctx.web.lists.get_by_title("Tasks").content_types.ensure(
        "Project", "desc", "Custom", content_type_id=_CT_ID
    ).execute_query()

    body = transport.requests[-1].data
    assert body["Name"] == "Project"
    assert body["Description"] == "desc"
    assert body["Group"] == "Custom"
    assert body["Id"]["StringValue"] == _CT_ID
    assert "__metadata" not in body["Group"]


_LINK_REJECTED = {
    "http_status": 400,
    "body": {
        "error": {
            "code": "-2147024809, System.ArgumentException",
            "message": {"lang": "en-US", "value": "Column 'ProjectType' does not exist."},
        }
    },
}


class _FieldLinks:
    """In-memory field links, so a read after a write sees what the write did.

    ``refuse`` names the column the server rejects; with ``atomic`` the rejection
    rolls the whole change set back, so nothing the batch wrote survives even
    though the sibling sub-responses still answer ``200``.
    """

    def __init__(self, seed=None, refuse=None, atomic=False):
        self._links = dict(seed or {})
        self._refuse = refuse
        self._atomic = atomic
        self._rolled_back = False

    def read(self, request):
        linked = [] if self._rolled_back else self._links.get(_ct_key(request.url), [])
        results = [{"Name": name, "FieldInternalName": name} for name in linked]
        return {"d": {"results": results}}

    def add(self, request):
        name = request.data["FieldInternalName"]
        if name == self._refuse:
            self._rolled_back = self._atomic
            return _LINK_REJECTED
        if not self._rolled_back:
            self._links.setdefault(_ct_key(request.url), []).append(name)
        return {"d": {"Name": name}}


def _ct_key(url):
    return url.split("/ContentTypes(")[-1].split(")")[0].strip("'")


def _link_routes(links=None):
    links = links if links is not None else _FieldLinks()
    return [
        (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        (HttpMethod.Get, "getByInternalNameOrTitle", _NOT_FOUND),
        (HttpMethod.Post, "CreateFieldAsXml", {"d": {"InternalName": "ProjectType", "FieldTypeKind": 6}}),
        # field links must be matched before the bare /ContentTypes routes
        (HttpMethod.Get, "/FieldLinks", links.read),
        (HttpMethod.Post, "/FieldLinks/Reorder", {}),
        (HttpMethod.Post, "/FieldLinks", links.add),
        (HttpMethod.Get, "ContentTypes?$filter=", {"d": {"results": []}}),
        (HttpMethod.Post, "/ContentTypes", {"d": {"Name": "Project", "StringId": _CT_ID}}),
        (HttpMethod.Get, "/ContentTypes", {"d": {"results": [{"Name": "Project", "StringId": _CT_ID}]}}),
    ]


def test_provision_reports_columns_the_server_refuses_to_link():
    ctx, transport = _setup(_link_routes(_FieldLinks(refuse="ProjectType")))

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure(views=[]))

    # ``Title`` is a built-in link left to the target; only the captured column is attempted
    assert len(warnings) == 1
    assert "ProjectType" in warnings[0]
    assert "was not linked" in warnings[0]
    # no reorder is attempted when nothing could be linked
    assert not any(u.endswith("/FieldLinks/Reorder") for u in _urls(transport))


def test_provision_reports_links_a_rejected_sibling_rolled_back():
    # The adds travel in one change set, which the server applies atomically: a
    # refused column takes its siblings with it while their sub-responses still
    # answer 200. The read-back is what turns that into warnings, so a silently
    # rolled-back link cannot be reported as linked.
    links = _FieldLinks(refuse="MediaServiceImageTags", atomic=True)
    ctx, transport = _setup(_link_routes(links))
    structure = _structure(
        views=[],
        fields=[
            FieldDefinition(internal_name="ProjectType", title="Project Type", field_type_kind=6, schema_xml="<Field/>"),
            FieldDefinition(
                internal_name="MediaServiceImageTags", title="Tags", field_type_kind=6, schema_xml="<Field/>"
            ),
        ],
        content_types=[
            ContentTypeDefinition(
                string_id=_CT_ID, name="Project", field_internal_names=["ProjectType", "MediaServiceImageTags"]
            )
        ],
    )

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert len(warnings) == _LINKED_COLUMNS
    assert "column 'ProjectType' was not linked" in warnings[0]
    # the refused column carries the server's reason, the rolled-back sibling cannot
    assert "column 'MediaServiceImageTags' was not linked: Column 'ProjectType' does not exist." in warnings[1]
    # a column the server does not hold cannot be ordered
    assert not any(u.endswith("/FieldLinks/Reorder") for u in _urls(transport))


def test_provision_skips_links_for_columns_it_did_not_capture():
    # A content type may link built-in columns (``Title``) that capture deliberately
    # skips; sending them to the server is a guaranteed ``does not exist`` failure.
    routes = _link_routes()
    ctx, transport = _setup(routes)
    structure = _structure(
        views=[],
        content_types=[
            ContentTypeDefinition(
                string_id=_CT_ID,
                name="Project",
                field_internal_names=["Title", "ProjectType", "MediaServiceImageTags"],
            )
        ],
    )

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert warnings == []
    linked = [r.data["FieldInternalName"] for r in _posts(transport) if r.url.endswith("/FieldLinks")]
    assert linked == ["ProjectType"]


def test_provision_reorders_links_with_a_plain_array():
    # the server already links both columns, but in the wrong order
    links = _FieldLinks(seed={_CT_ID: ["ProjectType", "Category"]})
    ctx, transport = _setup(_link_routes(links))
    structure = _structure(
        views=[],
        fields=[
            FieldDefinition(internal_name="ProjectType", title="Project Type", field_type_kind=6, schema_xml="<Field/>"),
            FieldDefinition(internal_name="Category", title="Category", field_type_kind=6, schema_xml="<Field/>"),
        ],
        content_types=[
            ContentTypeDefinition(string_id=_CT_ID, name="Project", field_internal_names=["Category", "ProjectType"])
        ],
    )

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    reorder = next(r for r in _posts(transport) if r.url.endswith("/FieldLinks/Reorder"))
    assert isinstance(reorder.data["internalNames"], list)
    assert reorder.data["internalNames"] == ["Category", "ProjectType"]


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


def test_rewrite_lookup_schema_reports_unresolved_list():
    rewritten, unresolved = rewrite_lookup_schema(_LOOKUP_SCHEMA, {})

    assert rewritten is None
    assert unresolved == _SOURCE_LIST_ID


def test_rewrite_lookup_schema_leaves_user_info_keyword_alone():
    schema = '<Field Type="User" List="UserInfo" Name="Owner"/>'

    assert rewrite_lookup_schema(schema, {}) == (schema, None)


def test_rewrite_lookup_schema_ignores_non_lookup_field():
    schema = '<Field Type="Choice" List="{A6879990-804B-4064-BF5D-F0C5C65EF768}"/>'

    assert rewrite_lookup_schema(schema, {}) == (schema, None)


def test_normalize_guid_strips_braces_and_lowercases():
    assert normalize_guid("{A6879990-804B-4064-BF5D-F0C5C65EF768}") == _SOURCE_LIST_ID
    assert normalize_guid(_SOURCE_LIST_ID) == _SOURCE_LIST_ID
    assert normalize_guid("UserInfo") is None
    assert normalize_guid(None) is None


def _lookup_routes():
    return [
        (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        (HttpMethod.Get, "getByInternalNameOrTitle", _NOT_FOUND),
        (HttpMethod.Post, "CreateFieldAsXml", {"d": {"InternalName": "Dept", "FieldTypeKind": 7}}),
    ]


def _lookup_structure():
    return _structure(
        fields=[FieldDefinition(internal_name="Dept", title="Dept", type_as_string="Lookup", schema_xml=_LOOKUP_SCHEMA)],
        content_types=[],
        views=[],
    )


def test_provision_creates_lookup_column_pointed_at_target_list():
    ctx, transport = _setup(_lookup_routes())

    warnings = provision_list_structure(
        ctx.web.lists.get_by_title("Tasks"), _lookup_structure(), list_id_map={_SOURCE_LIST_ID: _TARGET_LIST_ID}
    )

    assert warnings == []
    create = next(p for p in _posts(transport) if p.url.endswith("Fields/CreateFieldAsXml"))
    body = str(create.data)
    assert _TARGET_LIST_ID in body
    assert "A6879990" not in body


def test_provision_skips_lookup_into_a_list_outside_the_migration():
    ctx, transport = _setup(
        [
            (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        ]
    )

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _lookup_structure(), list_id_map={})

    assert len(warnings) == 1
    assert "Dept" in warnings[0]
    assert _SOURCE_LIST_ID in warnings[0]
    assert not any(p.url.endswith("Fields/CreateFieldAsXml") for p in _posts(transport))


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


def _taxonomy_structure(mult=""):
    schema = _TAXONOMY_SCHEMA.replace('Mult="FALSE"', f'Mult="{mult}"') if mult else _TAXONOMY_SCHEMA
    return _structure(
        fields=[
            FieldDefinition(
                internal_name="Dept",
                title="Dept",
                field_type_kind=21,
                type_as_string="TaxonomyFieldTypeMulti" if mult == "TRUE" else "TaxonomyFieldType",
                schema_xml=schema,
            )
        ],
        content_types=[],
        views=[],
    )


def _taxonomy_routes(existing=()):
    return [
        (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        # TaxonomyField.create first creates a hidden note column, then reads the
        # web id, then creates the taxonomy column itself.
        (HttpMethod.Post, "CreateFieldAsXml", {"d": {"Id": _NOTE_ID}}),
        (HttpMethod.Get, "/Web?", {"d": {"Id": _WEB_ID}}),
        (HttpMethod.Get, "/Fields", {"d": {"results": list(existing)}}),
    ]


def test_provision_recreates_a_taxonomy_column_against_the_term_set():
    ctx, transport = _setup(_taxonomy_routes())

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _taxonomy_structure())

    assert warnings == []
    creates = [p for p in _posts(transport) if p.url.endswith("CreateFieldAsXml")]
    note_create, taxonomy_create = creates
    note_schema, taxonomy_schema = str(note_create.data), str(taxonomy_create.data)
    assert 'Type="Note"' in note_schema
    assert 'Type="TaxonomyFieldType"' in taxonomy_schema
    assert "a83fe90d-4bdb-4644-a484-7f75ee3f5730" in taxonomy_schema
    assert _WEB_ID in taxonomy_schema
    # The source schema names the source web's TaxonomyHiddenList and note field;
    # replaying it verbatim would bind the copy to columns that do not exist here.
    assert "List=" not in taxonomy_schema
    assert "11111111-1111-1111-1111-111111111111" not in taxonomy_schema


def test_provision_skips_an_existing_taxonomy_column():
    ctx, transport = _setup(_taxonomy_routes(existing=[{"InternalName": "Dept"}]))

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _taxonomy_structure())

    assert [p for p in _posts(transport) if p.url.endswith("CreateFieldAsXml")] == []


def test_provision_multi_taxonomy_column_sets_the_mult_flag():
    ctx, transport = _setup(_taxonomy_routes())

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _taxonomy_structure(mult="TRUE"))

    taxonomy_schema = str([p for p in _posts(transport) if p.url.endswith("CreateFieldAsXml")][-1].data)
    assert 'Type="TaxonomyFieldTypeMulti"' in taxonomy_schema
    assert 'Mult="TRUE"' in taxonomy_schema


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


def test_provision_applies_settings_even_with_skip_conflict_mode():
    ctx, transport = _setup(_setting_routes())
    structure = _empty_structure(settings={"EnableModeration": True})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure, on_conflict="skip")

    assert _settings_written(transport) == [{"EnableModeration": True}]


def test_provision_leaves_settings_the_target_already_carries_alone():
    # A list created from its template already carries most settings; re-MERGEing an
    # equal value is a needless write (and SharePoint rejects some of them outright:
    # a version limit with versioning off, a system library that grants no write).
    ctx, transport = _setup(
        _setting_routes({"EnableVersioning": True, "MajorVersionLimit": 12, "EnableModeration": False})
    )
    structure = _empty_structure(settings={"EnableVersioning": True, "MajorVersionLimit": 12, "EnableModeration": False})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert _merges(transport) == []


def test_provision_writes_only_the_settings_that_differ():
    ctx, transport = _setup(_setting_routes({"EnableVersioning": True, "MajorVersionLimit": 500}))
    structure = _empty_structure(settings={"EnableVersioning": True, "MajorVersionLimit": 12})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert _settings_written(transport) == [{"MajorVersionLimit": 12}]


def test_provision_skips_a_version_limit_while_its_versioning_is_off():
    # The server rejects the limit outright ("Versioning must be enabled and the
    # number of major versions must be between 1 and 50000"), so it is not sent.
    ctx, transport = _setup(
        _setting_routes(
            {
                "EnableVersioning": False,
                "EnableMinorVersions": False,
                "MajorVersionLimit": 500,
                "MajorWithMinorVersionsLimit": 5,
            }
        )
    )
    structure = _empty_structure(
        settings={
            "EnableVersioning": False,
            "MajorVersionLimit": 12,
            "EnableMinorVersions": False,
            "MajorWithMinorVersionsLimit": 3,
        }
    )

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert _merges(transport) == []


def test_provision_applies_list_validation_after_the_columns_exist():
    ctx, transport = _setup([*_routes(), *_setting_routes()])
    structure = _structure(settings={"ValidationFormula": '=IF([Title]="",TRUE,FALSE)'})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    create = next(i for i, r in enumerate(transport.requests) if r.url.endswith("Fields/CreateFieldAsXml"))
    formula = next(
        i
        for i, r in enumerate(transport.requests)
        if isinstance(r.data, dict) and r.data.get("ValidationFormula") == '=IF([Title]="",TRUE,FALSE)'
    )
    assert formula > create


def test_provision_reports_a_rejected_setting_as_a_warning():
    transport = _RejectingSettingTransport(_setting_routes(), "EnableMinorVersions")
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    ctx.pending_request().transport = transport
    structure = _empty_structure(base_type=1, settings={"EnableMinorVersions": True, "ForceCheckout": True})

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert len(warnings) == 1
    assert "EnableMinorVersions" in warnings[0]
    # the rejected setting does not stop the ones after it
    assert {"ForceCheckout": True} in _settings_written(transport)


def test_provision_skips_library_only_settings_for_a_plain_list():
    ctx, transport = _setup([])
    structure = _empty_structure(base_type=0, settings={"ForceCheckout": True})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert _merges(transport) == []


def test_provision_skips_settings_when_the_list_has_no_title():
    ctx, transport = _setup([])
    structure = _empty_structure(title=None, settings={"EnableVersioning": True})

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), structure)

    assert _merges(transport) == []


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


def test_provision_leaves_matching_formatting_alone():
    ctx, transport = _setup(
        [
            (
                HttpMethod.Get,
                "Fields/getByInternalNameOrTitle('Status')",
                {"d": {"InternalName": "Status", "CustomFormatter": _COLUMN_FORMATTER}},
            ),
            (
                HttpMethod.Get,
                "views/GetByTitle('All Items')",
                {"d": {"Title": "All Items", "CustomFormatter": _VIEW_FORMATTER}},
            ),
        ]
    )

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _formatting_structure())

    assert [p for p in _posts(transport) if p.headers.get("X-HTTP-Method") == "MERGE"] == []
    assert not any("$select=InternalName" in u for u in _urls(transport))


def test_provision_reports_a_formatter_the_target_would_not_take():
    ctx, _ = _setup(_formatting_routes(field_read_back=None, view_read_back="{}"))

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _formatting_structure())

    assert "column 'Status' kept its own formatting: the target would not accept the formatter" in warnings
    assert "view 'All Items' kept its own formatting: the target would not accept the formatter" in warnings


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
