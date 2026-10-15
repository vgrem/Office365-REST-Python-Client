"""Offline tests for replaying a captured list structure onto a target list.

``provision_list_structure`` is imperative (it issues and executes requests), so
these tests script the request/response exchange with a small method-aware
routing transport. They assert both that the right endpoints are hit and that the
content-type field-link URLs are correctly pathed from the reloaded content type.
"""

from __future__ import annotations

from office365.migration.sharepoint.structure import (
    ContentTypeDefinition,
    FieldDefinition,
    ListStructure,
    ViewDefinition,
    provision_list_structure,
)
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import build_response

_CT_ID = "0x0100abcdefabcdefabcdefabcdefab"

_NOT_FOUND = {
    "http_status": 404,
    "body": {"error": {"code": "Request_ResourceNotFound", "message": "Resource not found"}},
}


class _MethodRoutingTransport(BaseTransport):
    """Routes by (HTTP method, URL substring), recording every request."""

    def __init__(self, routes):
        self._routes = routes
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        for method, key, payload in self._routes:
            if method is not None and request.method != method:
                continue
            if key in request.url:
                return build_response(request, payload)
        raise AssertionError(f"no route for {request.method} {request.url}")


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


def _setup(routes):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _MethodRoutingTransport(routes)
    ctx.pending_request().transport = transport
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
    assert sum(1 for p in _posts(transport) if p.url.endswith("/FieldLinks")) == 2  # noqa: PLR2004 (2 links)
    assert any(u.endswith("/FieldLinks/Reorder") for u in urls)
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


def _link_routes(link_payload):
    return [
        (HttpMethod.Get, "$select=ContentTypesEnabled", {"d": {"ContentTypesEnabled": True}}),
        (HttpMethod.Get, "getByInternalNameOrTitle", _NOT_FOUND),
        (HttpMethod.Post, "CreateFieldAsXml", {"d": {"InternalName": "ProjectType", "FieldTypeKind": 6}}),
        # field links must be matched before the bare /ContentTypes routes
        (HttpMethod.Get, "/FieldLinks", {"d": {"results": []}}),
        (HttpMethod.Post, "/FieldLinks/Reorder", {}),
        (HttpMethod.Post, "/FieldLinks", link_payload),
        (HttpMethod.Get, "ContentTypes?$filter=", {"d": {"results": []}}),
        (HttpMethod.Post, "/ContentTypes", {"d": {"Name": "Project", "StringId": _CT_ID}}),
        (HttpMethod.Get, "/ContentTypes", {"d": {"results": [{"Name": "Project", "StringId": _CT_ID}]}}),
    ]


def test_provision_reports_columns_the_server_refuses_to_link():
    ctx, transport = _setup(_link_routes(_LINK_REJECTED))

    warnings = provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure(views=[]))

    assert len(warnings) == 2  # both captured links were rejected  # noqa: PLR2004
    assert all("was not linked" in warning for warning in warnings)
    # no reorder is attempted when nothing could be linked
    assert not any(u.endswith("/FieldLinks/Reorder") for u in _urls(transport))


def test_provision_reorders_links_with_a_plain_array():
    ctx, transport = _setup(_link_routes({}))

    provision_list_structure(ctx.web.lists.get_by_title("Tasks"), _structure(views=[]))

    reorder = next(r for r in _posts(transport) if r.url.endswith("/FieldLinks/Reorder"))
    assert isinstance(reorder.data["internalNames"], list)
    assert reorder.data["internalNames"] == ["Title", "ProjectType"]
