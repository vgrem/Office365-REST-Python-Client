"""Offline tests for content-type field-ordering payloads.

Both ``ReorderFields`` and ``FieldLinks/Reorder`` take a raw JSON array of
internal names. Wrapping them as an OData ``Collection(Edm.String)`` object is
rejected by SharePoint Online ("...a node of type 'StartObject' was read ...
however, a 'StartArray' node was expected.").
"""

from __future__ import annotations

from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from tests import test_site_url
from tests._scripted_transport import build_response

_CT_ID = "0x0100abcdefabcdefabcdefabcdefab"


class _RecordingTransport(BaseTransport):
    """Records every request and answers 200 with an empty verbose body."""

    def __init__(self):
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return build_response(request, {"d": {}})


def _ctx():
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _RecordingTransport()
    ctx.pending_request().transport = transport
    return ctx, transport


def test_field_links_reorder_sends_a_plain_array():
    ctx, transport = _ctx()

    ctx.web.content_types.get_by_id(_CT_ID).field_links.reorder(["Title", "ProjectType"])
    ctx.execute_query()

    assert transport.requests[-1].data == {"internalNames": ["Title", "ProjectType"]}
