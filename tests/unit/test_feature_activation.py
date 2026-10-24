"""Offline tests for feature activation: `Site/Features` read, `Add` when missing.

``FeatureCollection.add(verify_if_activated=True)`` has to answer one question
before it writes: is the feature already active? The cheap-looking answer — a
``GetById`` whose payload is empty means "not activated" — is wrong at site
scope, where ``GetById`` answers ``null`` for *every* feature, activated or not.
Verified live: ``Site/Features/GetById('<guid>')`` returns
``{"d":{"GetById":null}}`` for a plain site, so a truthiness test on that payload
suppresses the activation for good. The activation state therefore comes from the
collection the operation reads anyway.
"""

from office365.runtime.http.http_method import HttpMethod
from office365.runtime.transport.base import BaseTransport
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.features.definitions.scope import FeatureDefinitionScope
from office365.sharepoint.features.known_list import KnownFeaturesList
from tests import test_site_url
from tests._scripted_transport import build_response

#: An activated feature that is *not* the one under test.
_OTHER_FEATURE = "3019c9b4-e371-438d-98f6-0a08c34d06eb"

#: The feature under test; the tenant in the probe does not install its definition.
_TARGET_FEATURE = KnownFeaturesList.PlaceRecordsManagement.value.lower()


class _FeatureTransport(BaseTransport):
    """Answers the feature collection read; records every request it receives."""

    def __init__(self, activated_ids):
        self._activated_ids = activated_ids
        self.requests = []

    def execute(self, request):
        self.requests.append(request)
        if request.method == HttpMethod.Post:
            return build_response(request, {"d": {"DefinitionId": _TARGET_FEATURE}})
        if "/GetById" in request.url:
            # What the live service answers at site scope, for any feature id.
            return build_response(request, {"d": {"GetById": None}})
        return build_response(
            request,
            {"d": {"results": [{"DefinitionId": feature_id} for feature_id in self._activated_ids]}},
        )

    @property
    def posts(self):
        return [request for request in self.requests if request.method == HttpMethod.Post]


def _ctx(activated_ids):
    ctx = ClientContext(test_site_url)
    ctx.pending_request().beforeExecute.clear()
    transport = _FeatureTransport(activated_ids)
    ctx.pending_request().transport = transport
    return ctx, transport


def test_add_activates_a_feature_the_collection_does_not_list():
    """A feature absent from the collection is activated, even though `GetById` is null."""
    ctx, transport = _ctx([_OTHER_FEATURE])

    ctx.site.features.add(_TARGET_FEATURE, False, FeatureDefinitionScope.Site, True).execute_query()

    assert not [request for request in transport.requests if "/GetById" in request.url]
    assert len(transport.posts) == 1
    assert transport.posts[0].data == {
        "featureId": _TARGET_FEATURE,
        "force": False,
        "featdefScope": FeatureDefinitionScope.Site,
    }


def test_add_leaves_an_activated_feature_alone():
    """A feature the collection already lists is not activated twice."""
    ctx, transport = _ctx([_OTHER_FEATURE, _TARGET_FEATURE])

    ctx.site.features.add(_TARGET_FEATURE, False, FeatureDefinitionScope.Site, True).execute_query()

    assert transport.posts == []


def test_add_without_verification_writes_straight_away():
    """`verify_if_activated=False` keeps the single-request form: no read first."""
    ctx, transport = _ctx([_TARGET_FEATURE])

    ctx.site.features.add(_TARGET_FEATURE, False, FeatureDefinitionScope.Site).execute_query()

    assert len(transport.requests) == 1
    assert transport.requests[0].method == HttpMethod.Post
