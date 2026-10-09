from __future__ import annotations

from datetime import datetime, timezone

from office365.sharepoint.listitems.listitem import ListItem
from office365.sharepoint.sharing.links.kind import SharingLinkKind


class _FakeContext:
    def __init__(self) -> None:
        self.queries = []

    def add_query(self, query) -> None:
        self.queries.append(query)


def _share_request(item: ListItem, **kwargs):
    item.share_link(SharingLinkKind.AnonymousView, **kwargs)
    return item.context.queries[-1]._parameters_type["request"]


def test_expiration_serialized_as_utc_with_z():
    item = ListItem(_FakeContext())
    request = _share_request(item, expiration=datetime(2026, 1, 1, 0, 0, 0, 123456, tzinfo=timezone.utc))
    assert request.to_json()["settings"]["expiration"] == "2026-01-01T00:00:00Z"


def test_expiration_omitted_when_none():
    item = ListItem(_FakeContext())
    request = _share_request(item)
    assert "expiration" not in request.to_json()["settings"]


def test_share_id_forwarded():
    item = ListItem(_FakeContext())
    share_id = "11111111-2222-3333-4444-555555555555"
    request = _share_request(item, share_id=share_id)
    assert request.to_json()["settings"]["shareId"] == share_id
