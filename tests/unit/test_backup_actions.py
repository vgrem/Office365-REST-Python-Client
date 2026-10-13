"""Offline tests for the Microsoft 365 Backup Storage surface.

Two things are covered:

* the CSDL-declared inheritance of the Backup Storage entities (the generator
  drops ``BaseType`` for this namespace, so the derived types used to extend
  ``Entity`` directly and missed the shared lifecycle helpers), and
* the request shape (method, URL and JSON body) of the hand-written action
  methods the library exposes for the service: ``activate``/``deactivate``,
  ``offboard``/``cancelOffboard``, ``run``/``deleteAndUnprotect``, ``browse``,
  ``search`` and the service-app ``activate``.

The tenant under test has no Backup Storage license, so these are deliberately
request-construction tests rather than live calls.
"""

from __future__ import annotations

from datetime import datetime

from office365.backuprestore.browse_session_base import BrowseSessionBase
from office365.backuprestore.onedrive_for_business_browse_session import (
    OneDriveForBusinessBrowseSession,
)
from office365.backuprestore.onedrive_for_business_restore_session import (
    OneDriveForBusinessRestoreSession,
)
from office365.backuprestore.protection_unit_base import ProtectionUnitBase
from office365.backuprestore.restorepoints.collection import RestorePointCollection
from office365.backuprestore.restorepoints.preference import RestorePointPreference
from office365.backuprestore.restorepoints.tags import RestorePointTags
from office365.backuprestore.restoresessions.browsable_resource_type import (
    BrowsableResourceType,
)
from office365.backuprestore.restoresessions.browse_query_order import BrowseQueryOrder
from office365.backuprestore.serviceapps.service_app import ServiceApp
from office365.backuprestore.sharepoint_browse_session import SharePointBrowseSession
from office365.backuprestore.sharepoint_protection_policy import SharePointProtectionPolicy
from office365.backuprestore.sharepoint_restore_session import SharePointRestoreSession
from office365.common.drive_protection_unit import DriveProtectionUnit
from office365.common.exchange_protection_policy import ExchangeProtectionPolicy
from office365.common.exchange_restore_session import ExchangeRestoreSession
from office365.common.mailbox_protection_rule import MailboxProtectionRule
from office365.common.mailbox_protection_unit import MailboxProtectionUnit
from office365.common.restore_point import RestorePoint
from office365.common.restore_session_base import RestoreSessionBase
from office365.common.site_protection_rule import SiteProtectionRule
from office365.common.site_protection_unit import SiteProtectionUnit
from office365.directory.protection.policy.base import ProtectionPolicyBase
from office365.directory.protection.rules.base import ProtectionRuleBase
from office365.graph_client import GraphClient
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.paths.resource_path import ResourcePath
from tests._scripted_transport import ScriptedTransport

EMPTY_ITEMS = {"value": []}


class _RecordingTransport(ScriptedTransport):
    """Scripted transport that also records the requests it received."""

    def __init__(self):
        super().__init__([EMPTY_ITEMS] * 20)
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        return super().execute(request)


def _client():
    transport = _RecordingTransport()
    client = GraphClient()
    client.pending_request().beforeExecute.clear()
    client.pending_request().transport = transport
    return client, transport


def _last(transport):
    request = transport.requests[-1]
    assert request.method == HttpMethod.Post
    return request


# --- inheritance (guards the CSDL BaseType the generator omits) -------------


def test_backup_entities_follow_csdl_inheritance():
    assert issubclass(SharePointProtectionPolicy, ProtectionPolicyBase)
    assert issubclass(ExchangeProtectionPolicy, ProtectionPolicyBase)
    assert issubclass(SharePointBrowseSession, BrowseSessionBase)
    assert issubclass(OneDriveForBusinessBrowseSession, BrowseSessionBase)
    assert issubclass(SharePointRestoreSession, RestoreSessionBase)
    assert issubclass(OneDriveForBusinessRestoreSession, RestoreSessionBase)
    assert issubclass(ExchangeRestoreSession, RestoreSessionBase)
    assert issubclass(DriveProtectionUnit, ProtectionUnitBase)
    assert issubclass(MailboxProtectionUnit, ProtectionUnitBase)
    assert issubclass(SiteProtectionUnit, ProtectionUnitBase)
    assert issubclass(MailboxProtectionRule, ProtectionRuleBase)
    assert issubclass(SiteProtectionRule, ProtectionRuleBase)


# --- protection policies ----------------------------------------------------


def test_protection_policy_activate_and_deactivate():
    client, transport = _client()
    SharePointProtectionPolicy(client, ResourcePath("protectionPolicies/1")).activate().execute_query()
    SharePointProtectionPolicy(client, ResourcePath("protectionPolicies/1")).deactivate().execute_query()

    assert _last(transport).url.endswith("/protectionPolicies/1/deactivate")
    assert transport.requests[0].url.endswith("/protectionPolicies/1/activate")


# --- restore sessions -------------------------------------------------------


def test_restore_session_activate():
    client, transport = _client()
    SharePointRestoreSession(client, ResourcePath("restoreSessions/1")).activate().execute_query()
    assert _last(transport).url.endswith("/restoreSessions/1/activate")


# --- protection units -------------------------------------------------------


def test_protection_unit_offboard_and_cancel():
    client, transport = _client()
    MailboxProtectionUnit(client, ResourcePath("protectionUnits/1")).offboard().execute_query()
    MailboxProtectionUnit(client, ResourcePath("protectionUnits/1")).cancel_offboard().execute_query()

    assert _last(transport).url.endswith("/protectionUnits/1/cancelOffboard")
    assert transport.requests[0].url.endswith("/protectionUnits/1/offboard")


# --- protection rules -------------------------------------------------------


def test_protection_rule_run_and_delete():
    client, transport = _client()
    SiteProtectionRule(client, ResourcePath("siteInclusionRules/1")).run().execute_query()
    SiteProtectionRule(client, ResourcePath("siteInclusionRules/1")).delete_and_unprotect().execute_query()

    assert _last(transport).url.endswith("/siteInclusionRules/1/deleteAndUnprotect")
    assert transport.requests[0].url.endswith("/siteInclusionRules/1/run")


# --- browse session ---------------------------------------------------------


def test_browse_session_builds_typed_payload():
    client, transport = _client()
    SharePointBrowseSession(client, ResourcePath("browseSessions/1")).browse(
        "item-key", BrowsableResourceType.folder, "name eq 'report'", BrowseQueryOrder.nameDsc
    ).execute_query()

    request = _last(transport)
    assert request.url.endswith("/browseSessions/1/browse")
    assert request.data == {
        "browseLocationItemKey": "item-key",
        "browseResourceType": "folder",
        "filter": "name eq 'report'",
        "orderBy": "nameDsc",
    }


def test_browse_session_omits_unset_optional_parameters():
    client, transport = _client()
    SharePointBrowseSession(client, ResourcePath("browseSessions/1")).browse(
        "item-key", BrowsableResourceType.site
    ).execute_query()
    assert _last(transport).data == {"browseLocationItemKey": "item-key", "browseResourceType": "site"}


# --- service apps -----------------------------------------------------------


def test_service_app_activate_formats_utc_datetime():
    client, transport = _client()
    ServiceApp(client, ResourcePath("serviceApps/1")).activate(datetime(2024, 1, 2, 3, 4, 5)).execute_query()

    request = _last(transport)
    assert request.url.endswith("/serviceApps/1/activate")
    assert request.data == {"effectiveDateTime": "2024-01-02T03:04:05Z"}


def test_service_app_deactivate():
    client, transport = _client()
    ServiceApp(client, ResourcePath("serviceApps/1")).deactivate().execute_query()
    assert _last(transport).url.endswith("/serviceApps/1/deactivate")


# --- restore-point search ---------------------------------------------------


def test_restore_points_search_serializes_enum_names():
    client, transport = _client()
    RestorePointCollection(client, RestorePoint, ResourcePath("restorePoints")).search(
        protection_unit_ids=["pu-1", "pu-2"],
        restore_point_preference=RestorePointPreference.latest,
        tags=RestorePointTags.fastRestore,
    ).execute_query()

    request = _last(transport)
    assert request.url.endswith("/restorePoints/search")
    assert request.data == {
        "protectionUnitIds": ["pu-1", "pu-2"],
        "restorePointPreference": "latest",
        "tags": "fastRestore",
    }


def test_restore_points_search_omits_unset_filters():
    client, transport = _client()
    RestorePointCollection(client, RestorePoint, ResourcePath("restorePoints")).search().execute_query()
    assert _last(transport).data == {}


def test_root_exposes_restore_point_collection():
    client, transport = _client()
    collection = client.solutions.backup_restore.restore_points
    assert isinstance(collection, RestorePointCollection)

    collection.search(tags=RestorePointTags.none).execute_query()
    assert _last(transport).url.endswith("/restorePoints/search")
