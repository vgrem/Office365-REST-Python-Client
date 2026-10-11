"""Offline tests for asynchronous (HTTP 202) channel creation.

Creating a private or shared channel can return ``202 Accepted`` with a
``teamsAsyncOperation``. ``ChannelCollection.add`` must follow that operation
and load the finished channel, so ``channel.id`` is populated when
``execute_query()`` returns.

The operation's ``targetResourceId`` is the **team** id, while the channel URL
lives in ``targetResourceLocation`` — the regression this test pins down.
"""

from __future__ import annotations

from office365.graph_client import GraphClient
from office365.runtime.paths.resource_path import ResourcePath
from office365.teams.channels.collection import ChannelCollection
from tests._scripted_transport import ScriptedTransport

_CHANNEL_ID = "19:abc@thread.tacv2"

# Live Graph returns the operation and resource locations as root-relative paths.
_ACCEPTED = {
    "http_status": 202,
    "headers": {"Location": "/teams/t1/operations/op1"},
    "body": {},
}
_OPERATION_SUCCEEDED = {
    "http_status": 200,
    "headers": {"Content-Type": "application/json"},
    "body": {
        "status": "succeeded",
        # targetResourceId is the *team* id, not the channel id.
        "targetResourceId": "t1",
        "targetResourceLocation": f"/teams('t1')/channels('{_CHANNEL_ID}')",
    },
}
_CHANNEL = {
    "http_status": 200,
    "headers": {"Content-Type": "application/json"},
    "body": {"id": _CHANNEL_ID, "displayName": "Verify", "membershipType": "shared"},
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


def _channels(client: GraphClient) -> ChannelCollection:
    team_path = ResourcePath("t1", ResourcePath("teams"))
    return ChannelCollection(client, ResourcePath("channels", team_path))


def test_add_async_channel_follows_operation():
    transport = _RecordingTransport([_ACCEPTED, _OPERATION_SUCCEEDED, _CHANNEL])
    client = _client(transport)

    channel = _channels(client).add("Verify", membership_type="shared").execute_query()

    assert transport.calls == 3  # noqa: PLR2004
    assert channel.id == _CHANNEL_ID
    assert channel.display_name == "Verify"


def test_add_async_channel_loads_through_target_resource_location():
    transport = _RecordingTransport([_ACCEPTED, _OPERATION_SUCCEEDED, _CHANNEL])
    client = _client(transport)

    _channels(client).add("Verify", membership_type="shared").execute_query()

    # Poll the operation, then GET the channel from targetResourceLocation.
    assert transport.requests[1].url.endswith("/teams/t1/operations/op1")
    assert transport.requests[-1].url.endswith(f"/teams/t1/channels/{_CHANNEL_ID}")
