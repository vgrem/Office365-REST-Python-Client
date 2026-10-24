from __future__ import annotations

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.tenant.administration.tenant import Tenant

from tests import (
    answered_null,
    test_admin_site_url,
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestHomeSites(SPTestCase):
    """Home site management tests"""

    @classmethod
    def setUpClass(cls):
        client = ClientContext(test_admin_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
        cls.tenant = Tenant(client)

    def test_01_get_home_sites(self):
        """Get home sites.

        A tenant with no designated home site answers ``GetHomeSites: null`` rather
        than an empty collection.
        """
        result = self.tenant.get_home_sites().execute_query()
        if answered_null(result):
            self.skipTest("The tenant has not designated a home site")
        self.assertIsNotNone(result.value)
