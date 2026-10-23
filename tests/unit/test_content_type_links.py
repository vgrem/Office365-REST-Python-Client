"""Offline tests for a list's default content type (root folder order)."""

from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.contenttypes.content_type import _content_type_order_ids
from office365.sharepoint.contenttypes.content_type_id import ContentTypeId
from tests import test_site_url
from tests._scripted_transport import build_response


def test_order_ids_from_flattened_value():
    # The folder property is typed as a single ContentTypeId, so a server-side
    # Collection(SP.ContentTypeId) arrives flattened under numeric keys.
    order = ContentTypeId()
    order.set_property(0, {"StringValue": "0x02"})
    order.set_property(1, {"StringValue": "0x01"})
    assert _content_type_order_ids(order) == ["0x02", "0x01"]


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
