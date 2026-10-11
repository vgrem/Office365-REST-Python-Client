"""Offline tests for the ``POST /teams`` payload built by ``TeamCollection``.

Application-context team creation must name at least one owner, so
``create``/``create_and_wait`` accept an ``owners`` argument that is rendered as
``aadUserConversationMember`` entries in the request body.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from tests._scripted_transport import ScriptedTransport

_OPERATION = {
    "http_status": 202,
    "headers": {"Location": "https://graph.microsoft.com/v1.0/teams/abc/operations/op1"},
    "body": {},
}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _client(transport) -> GraphClient:
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client


def test_create_without_owners_omits_members():
    transport = _RecordingTransport([_OPERATION])
    client = _client(transport)

    client.teams.create("Team A", "desc").execute_query()

    body = transport.requests[-1].data
    assert transport.requests[-1].url.endswith("/teams")
    assert body["displayName"] == "Team A"
    assert body["description"] == "desc"
    assert "members" not in body


def test_create_with_owners_adds_conversation_members():
    transport = _RecordingTransport([_OPERATION])
    client = _client(transport)

    client.teams.create("Team A", "desc", "standard", owners=["ada@contoso.com"]).execute_query()

    assert transport.requests[-1].data["members"] == [
        {
            "@odata.type": "#microsoft.graph.aadUserConversationMember",
            "roles": ["owner"],
            "user@odata.bind": "https://graph.microsoft.com/v1.0/users('ada@contoso.com')",
        }
    ]
