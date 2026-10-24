"""Tests for SharePoint Business Data Connectivity (BDC) catalog operations."""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.sharepoint.client_context import ClientContext

from tests import test_admin_credentials, test_admin_site_url, test_client_id, test_tenant
from tests.sharepoint.sharepoint_case import SPTestCase


class TestBdc(SPTestCase):
    """Tests for BDC (Business Data Connectivity) operations."""

    app_site_url: ClassVar[Optional[str]] = None

    def test_01_get_corporate_catalog_url(self):
        """Get the corporate catalog URL from tenant settings."""
        admin_client = ClientContext(test_admin_site_url).with_username_and_password(
            test_tenant, test_client_id, test_admin_credentials.userName, test_admin_credentials.password
        )
        return_type = admin_client.tenant_settings.get().execute_query()
        self.assertIsNotNone(return_type.corporate_catalog_url)
        TestBdc.app_site_url = return_type.corporate_catalog_url

    # def test2_get_app_bdc_catalog(self):
    #    client = ClientContext(self.app_site_url).with_credentials(
    #        test_admin_credentials
    #    )
    #    result = client.web.get_app_bdc_catalog().execute_query()
    #    self.assertIsNotNone(result.resource_path)
