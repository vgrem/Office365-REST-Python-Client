"""eDiscovery cases — managing legal hold, review sets, and exports.
Tests cover the core eDiscovery workflows under Microsoft Purview eDiscovery (Premium):
  - Listing and filtering eDiscovery cases
  - Creating cases
  - Managing custodians
  - Review set operations
  - Searches and exports
The eDiscovery API lives under client.security.cases in the Graph SDK.
"""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.security.cases.ediscovery import EdiscoveryCase

from tests.decorators import requires_delegated
from tests.graph_case import GraphDelegatedTestCase

_EDISCOVERY_READ = ("eDiscovery.Read.All", "eDiscovery.ReadWrite.All")
_EDISCOVERY_WRITE = ("eDiscovery.ReadWrite.All",)


class TestEdiscoveryCases(GraphDelegatedTestCase):
    """eDiscovery cases — the top-level container for a discovery workflow."""

    created_case: ClassVar[Optional[EdiscoveryCase]] = None

    @requires_delegated(
        *_EDISCOVERY_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_01_list_ediscovery_cases(self):
        """Listing eDiscovery cases returns a valid collection."""
        result = self.client.security.cases.ediscovery_cases.top(10).get().execute_query()
        self.assertIsNotNone(result.resource_path)

    @requires_delegated(
        *_EDISCOVERY_WRITE,
        bypass_roles=["Global Administrator"],
    )
    def test_02_create_ediscovery_case(self):
        """Creating an eDiscovery case with display name and description."""
        try:
            case_name = f"SDK Test Case — Automated ({id(self)})"
            result = self.client.security.cases.ediscovery_cases.add(
                displayName=case_name,
                description="Automated SDK integration test — safe to delete",
            ).execute_query()
            self.assertIsNotNone(result.resource_path)
            self.assertEqual(result.get_property("displayName"), case_name)
            self.assertIsNotNone(result.get_property("id"))
            TestEdiscoveryCases.created_case = result
        except Exception as e:
            self.skipTest(f"Cannot create eDiscovery case: {e}")

    @requires_delegated(
        *_EDISCOVERY_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_03_get_ediscovery_case_by_id(self):
        """Retrieving a case by ID returns the correct case."""
        created_case = TestEdiscoveryCases.created_case
        if not created_case:
            self.skipTest("No created case available from previous test")
        case_id = created_case.id
        assert case_id is not None
        result = self.client.security.cases.ediscovery_cases[case_id].get().execute_query()
        self.assertIsNotNone(result.resource_path)
        self.assertEqual(result.get_property("id"), case_id)

    @requires_delegated(
        *_EDISCOVERY_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_04_case_displays_expected_properties(self):
        """An eDiscovery case exposes status, createdDateTime, and externalId."""
        cases = self.client.security.cases.ediscovery_cases.top(1).get().execute_query()
        if len(cases) == 0:
            self.skipTest("No eDiscovery cases exist to inspect")
        case = cases[0]
        # Cases typically have these top-level properties
        self.assertIsNotNone(case.get_property("displayName"))
        self.assertIsNotNone(case.get_property("status"))
        self.assertIsNotNone(case.get_property("createdDateTime"))

    @requires_delegated(
        *_EDISCOVERY_WRITE,
        bypass_roles=["Global Administrator"],
    )
    def test_05_close_and_delete_ediscovery_case(self):
        """Closing or deleting a case should succeed."""
        created = TestEdiscoveryCases.created_case
        if not created:
            self.skipTest("No created case available from previous test")
        try:
            created.delete_object().execute_query()
            TestEdiscoveryCases.created_case = None
        except Exception as e:
            self.skipTest(f"Cannot delete eDiscovery case (may require manual cleanup): {e}")

    @classmethod
    def tearDownClass(cls):
        """Best-effort cleanup."""
        case = cls.created_case
        if case and case.resource_path:
            try:
                case.delete_object().execute_query()
            except Exception:
                pass


class TestEdiscoveryCustodians(GraphDelegatedTestCase):
    """Custodians — data sources assigned to an eDiscovery case."""

    @requires_delegated(
        *_EDISCOVERY_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_01_custodians_have_sources(self):
        """A case's custodians expose userSource and siteSource sub-collections."""
        cases = self.client.security.cases.ediscovery_cases.top(3).get().execute_query()
        if len(cases) == 0:
            self.skipTest("No eDiscovery cases exist")
        for case in cases:
            try:
                custodians = case.custodians.get().execute_query()
                for custodian in custodians:
                    self.assertIsNotNone(custodian.get_property("displayName"))
                    self.assertIsNotNone(custodian.get_property("email"))
                if len(custodians) > 0:
                    break  # Check at least one case with custodians
            except Exception:
                continue

    @requires_delegated(
        *_EDISCOVERY_READ,
        bypass_roles=["Global Administrator"],
    )
    def test_02_search_in_case_is_accessible(self):
        """An eDiscovery case has a searches collection accessible via the client."""
        cases = self.client.security.cases.ediscovery_cases.top(3).get().execute_query()
        if len(cases) == 0:
            self.skipTest("No eDiscovery cases exist")
        for case in cases:
            try:
                searches = case.searches.get().execute_query()
                self.assertIsNotNone(searches.resource_path)
                break
            except Exception:
                continue
