"""Offline tests for the Graph ``find_by_*`` lookup helpers.

Every lookup is *deferred* (nothing hits the wire until ``execute_query()``) and
*tolerant* by default: a miss leaves the returned entity uninitialized instead
of raising, detected via ``is_loaded``. Pass ``required=True`` for the strict
``single`` semantics.
"""

from __future__ import annotations

from urllib.parse import unquote_plus

import pytest
from office365.booking.business.business import BookingBusiness
from office365.directory.licenses.subscribed_sku import SubscribedSku
from office365.directory.users.user import User
from office365.graph_client import GraphClient
from office365.intune.devices.management.managed.managed import ManagedDevice
from office365.runtime.types.exceptions import NotFoundException
from office365.teams.team import Team
from tests._scripted_transport import ScriptedTransport

USER = {"id": "u1", "displayName": "Ada Lovelace", "mail": "ada@contoso.com"}
TODO_TASK = {"id": "tt1", "title": "Ship the release"}
MAIL_FOLDER = {"id": "mf1", "displayName": "Archive"}
NOTEBOOK = {"id": "nb1", "displayName": "SDK OneNote Tour"}
SECTION = {"id": "sec1", "displayName": "SDK Examples"}
PLANNER_TASK = {"id": "pkt1", "title": "Draft the plan"}
PLANNER_BUCKET = {"id": "pbk1", "name": "Backlog"}
TEAM = {"id": "g1", "displayName": "Team One", "resourceProvisioningOptions": ["Team"]}
BUSINESS = {"id": "b1", "displayName": "Contoso Bookings"}
DEVICE = {"id": "d1", "deviceName": "DESKTOP-1"}
SKU = {"id": "s1", "skuId": "sku-guid", "skuPartNumber": "ENTERPRISEPACK"}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the request URLs it received."""

    def __init__(self, payloads):
        super().__init__(payloads)
        self.urls: list[str] = []

    def execute(self, request):
        self.urls.append(request.url)
        return super().execute(request)


def _client(payloads):
    transport = _RecordingTransport(payloads)
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


@pytest.mark.parametrize(
    ("lookup", "key", "payload"),
    [
        (lambda client: client.users.find_by_mail, "nobody@contoso.com", {"value": []}),
        (lambda client: client.teams.find_by_name, "Missing Team", {"value": []}),
        (lambda client: client.device_management.managed_devices.find_by_name, "NOPE", {"value": []}),
        (lambda client: client.subscribed_skus.find_by_part_number, "NOT_A_SKU", {"value": [SKU]}),
    ],
)
def test_lookup_miss_leaves_entity_uninitialized(lookup, key, payload):
    client, _ = _client([payload])

    entity = lookup(client)(key).execute_query()

    assert not entity.is_loaded
    assert entity.get_property("id") is None


@pytest.mark.parametrize(
    ("lookup", "key", "payload", "entity_id", "path", "filter_fragment"),
    [
        (
            lambda c: c.me.todo.lists["l1"].tasks.find_by_title,
            "Ship the release",
            TODO_TASK,
            "tt1",
            "/me/todo/lists/l1/tasks",
            "title eq 'Ship the release'",
        ),
        (
            lambda c: c.me.mail_folders.find_by_display_name,
            "Archive",
            MAIL_FOLDER,
            "mf1",
            "/me/mailFolders",
            "displayName eq 'Archive'",
        ),
        (
            lambda c: c.me.onenote.notebooks.find_by_display_name,
            "SDK OneNote Tour",
            NOTEBOOK,
            "nb1",
            "/me/onenote/notebooks",
            "displayName eq 'SDK OneNote Tour'",
        ),
        (
            lambda c: c.me.onenote.sections.find_by_display_name,
            "SDK Examples",
            SECTION,
            "sec1",
            "/me/onenote/sections",
            "displayName eq 'SDK Examples'",
        ),
    ],
)
def test_named_find_by_defers_and_returns_match(lookup, key, payload, entity_id, path, filter_fragment):
    client, transport = _client([{"value": [payload]}])

    entity = lookup(client)(key)

    assert transport.urls == []
    assert not entity.is_loaded

    entity.execute_query()

    assert entity.is_loaded
    assert entity.get_property("id") == entity_id
    url = unquote_plus(transport.urls[0])
    assert path in url
    assert filter_fragment in url


@pytest.mark.parametrize(
    "lookup",
    [
        lambda c: c.me.todo.lists["l1"].tasks.find_by_title,
        lambda c: c.me.mail_folders.find_by_display_name,
        lambda c: c.me.onenote.notebooks.find_by_display_name,
        lambda c: c.me.onenote.sections.find_by_display_name,
    ],
)
def test_named_find_by_miss_leaves_entity_uninitialized(lookup):
    client, _ = _client([{"value": []}])

    entity = lookup(client)("Missing").execute_query()

    assert not entity.is_loaded
    assert entity.get_property("id") is None


def test_find_by_title_escapes_single_quote():
    """An embedded apostrophe is doubled inside the OData string literal."""
    client, transport = _client([{"value": []}])

    client.me.todo.lists["l1"].tasks.find_by_title("O'Brien's task").execute_query()

    assert "title eq 'O''Brien''s task'" in unquote_plus(transport.urls[0])


def test_planner_task_find_by_title_matches_client_side():
    client, transport = _client([{"id": "p1", "title": "Plan"}, {"value": [PLANNER_TASK]}])
    plan = client.planner.plans["p1"].get().execute_query()

    task = plan.tasks.find_by_title("Draft the plan")

    assert len(transport.urls) == 1  # deferred: only the plan read so far
    assert not task.is_loaded

    task.execute_query()

    assert task.is_loaded
    assert task.get_property("id") == "pkt1"
    url = unquote_plus(transport.urls[1])
    assert "/planner/plans/p1/tasks" in url
    # Graph ignores $filter on a plan's tasks, so the match is client-side.
    assert "$filter" not in url


def test_planner_task_find_by_title_miss_is_client_side():
    client, _ = _client([{"id": "p1", "title": "Plan"}, {"value": [{"id": "pkt2", "title": "Other"}]}])
    plan = client.planner.plans["p1"].get().execute_query()

    task = plan.tasks.find_by_title("Draft the plan").execute_query()

    assert not task.is_loaded


def test_planner_bucket_find_by_name_matches_client_side():
    client, transport = _client([{"id": "p1", "title": "Plan"}, {"value": [PLANNER_BUCKET]}])
    plan = client.planner.plans["p1"].get().execute_query()

    bucket = plan.buckets.find_by_name("Backlog")

    assert len(transport.urls) == 1
    assert not bucket.is_loaded

    bucket.execute_query()

    assert bucket.is_loaded
    assert bucket.get_property("id") == "pbk1"
    url = unquote_plus(transport.urls[1])
    assert "/planner/plans/p1/buckets" in url
    # Graph ignores $filter on a plan's buckets, so the match is client-side.
    assert "$filter" not in url


def test_planner_bucket_find_by_name_miss_is_client_side():
    client, _ = _client([{"id": "p1", "title": "Plan"}, {"value": [{"id": "pbk2", "name": "Other"}]}])
    plan = client.planner.plans["p1"].get().execute_query()

    bucket = plan.buckets.find_by_name("Backlog").execute_query()

    assert not bucket.is_loaded


def test_user_plans_are_addressed_at_the_canonical_set():
    """Items listed via ``me/planner/plans`` are addressed at ``/planner/plans/{id}``.

    Graph rejects the nested ``/me/planner/plans/{id}/buckets`` navigation, so the
    item path must be the canonical top-level one for nested reads to resolve.
    """
    client, _ = _client([{"value": [{"id": "p1", "title": "Plan"}]}])

    plan = client.me.planner.plans.get().execute_query()[0]

    assert str(plan.resource_path) == "/planner/plans/p1"


def test_find_by_mail_defers_and_returns_match():
    client, transport = _client([{"value": [USER]}])

    user = client.users.find_by_mail("ada@contoso.com")

    assert transport.urls == []
    assert not user.is_loaded

    user.execute_query()

    assert isinstance(user, User)
    assert user.is_loaded
    assert user.get_property("id") == "u1"
    assert len(transport.urls) == 1
    assert "/users" in transport.urls[0]
    assert "mail eq 'ada@contoso.com'" in unquote_plus(transport.urls[0])


def test_team_find_by_name_defers_and_returns_team():
    client, transport = _client([{"value": [TEAM]}])

    team = client.teams.find_by_name("Team One")

    assert transport.urls == []
    assert not team.is_loaded

    team.execute_query()

    assert isinstance(team, Team)
    assert team.is_loaded
    assert team.get_property("id") == "g1"
    url = unquote_plus(transport.urls[0])
    assert "/groups" in url
    assert "resourceProvisioningOptions/Any(x:x eq 'Team')" in url
    assert "displayName eq 'Team One'" in url


def test_team_find_by_name_required_raises_on_miss():
    client, _ = _client([{"value": []}])

    client.teams.find_by_name("Missing Team", required=True)

    with pytest.raises(NotFoundException):
        client.execute_query()


def test_team_find_by_name_sets_entity_path_from_group_id():
    client, _ = _client([{"value": [TEAM]}])

    team = client.teams.find_by_name("Team One").execute_query()

    assert team.resource_url.endswith("/teams/g1")


def test_booking_find_by_name_matches_client_side():
    client, transport = _client([{"value": [{"id": "b0", "displayName": "Other"}, BUSINESS]}])

    business = client.solutions.booking_businesses.find_by_name("Contoso Bookings")

    assert transport.urls == []
    assert not business.is_loaded

    business.execute_query()

    assert isinstance(business, BookingBusiness)
    assert business.is_loaded
    assert business.get_property("id") == "b1"
    assert "/solutions/bookingBusinesses" in transport.urls[0]
    assert "$filter" not in transport.urls[0]


def test_booking_find_by_name_uninitialized_when_absent():
    client, _ = _client([{"value": [{"id": "b0", "displayName": "Other"}]}])

    business = client.solutions.booking_businesses.find_by_name("Missing").execute_query()

    assert not business.is_loaded


def test_managed_device_find_by_name_defers_and_returns_device():
    client, transport = _client([{"value": [DEVICE]}])

    device = client.device_management.managed_devices.find_by_name("DESKTOP-1")

    assert transport.urls == []
    assert not device.is_loaded

    device.execute_query()

    assert isinstance(device, ManagedDevice)
    assert device.is_loaded
    assert device.get_property("id") == "d1"
    url = unquote_plus(transport.urls[0])
    assert "/deviceManagement/managedDevices" in url
    assert "deviceName eq 'DESKTOP-1'" in url


def test_subscribed_sku_find_by_part_number_is_case_insensitive():
    client, transport = _client([{"value": [SKU]}])

    sku = client.subscribed_skus.find_by_part_number("enterprisepack")

    assert transport.urls == []
    assert not sku.is_loaded

    sku.execute_query()

    assert isinstance(sku, SubscribedSku)
    assert sku.is_loaded
    assert sku.get_property("id") == "s1"
    assert "/subscribedSkus" in transport.urls[0]


def test_find_by_mail_escapes_single_quote():
    """An embedded apostrophe is doubled inside the OData string literal."""
    client, transport = _client([{"value": []}])

    client.users.find_by_mail("o'brien@contoso.com").execute_query()

    assert "mail eq 'o''brien@contoso.com'" in unquote_plus(transport.urls[0])


def test_managed_device_first_or_none_contains_filter_runs_server_side():
    """The managed-device examples match a device-name substring via ``contains``."""
    client, transport = _client([{"value": [DEVICE]}])

    device = client.device_management.managed_devices.first_or_none("contains(deviceName, 'DESK')").execute_query()

    assert device.is_loaded
    assert device.get_property("id") == "d1"
    url = unquote_plus(transport.urls[0])
    assert "/deviceManagement/managedDevices" in url
    assert "contains(deviceName, 'DESK')" in url
    assert "$top=1" in url
