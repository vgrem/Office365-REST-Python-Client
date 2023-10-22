import uuid

from office365.sharepoint.lists.template_type import ListTemplateType
from office365.sharepoint.portal.sites.creation_response import SPSiteCreationResponse
from office365.sharepoint.portal.sites.status import SiteStatus
from office365.sharepoint.sites.site import Site
from tests import test_admin_credentials, test_site_url, test_user_principal_name_alt
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSite(SPTestCase):
    site_response = None  # type: SPSiteCreationResponse

    def test1_if_site_loaded(self):
        site = self.client.site.get().execute_query()
        self.assertIs(
            site.is_property_available("Url"), True, "Site resource was not requested"
        )
        self.assertIs(site.is_property_available("RootWeb"), False)

    def test2_if_site_exists(self):
        site_url = self.client.site.url
        result = Site.exists(self.client, site_url).execute_query()
        self.assertIsNotNone(result.value)

    def test3_get_site_by_id(self):
        site_id = self.client.site.id
        result = Site.get_url_by_id(self.client, site_id).execute_query()
        self.assertIsNotNone(result.value)

    def test4_get_site_catalog(self):
        catalog = (
            self.client.site.get_catalog(ListTemplateType.AppDataCatalog)
            .get()
            .execute_query()
        )
        self.assertIsNotNone(catalog.title)

    def test5_get_web_templates(self):
        web_templates = self.client.site.get_web_templates().execute_query()
        self.assertIsNotNone(web_templates)

    def test6_get_web_template_by_name(self):
        template_name = "GLOBAL#0"
        web_template = (
            self.client.site.get_web_templates()
            .get_by_name(template_name)
            .get()
            .execute_query()
        )
        self.assertIsNotNone(web_template)

    def test7_get_site_logo(self):
        result = self.client.site.get_site_logo().execute_query()
        self.assertIsNotNone(result.value)

    def test8_get_available_tags(self):
        result = self.client.site.get_available_tags().execute_query()
        self.assertIsNotNone(result.value)

    def test9_open_web_by_id(self):
        web = self.client.web.get().execute_query()
        sub_site = self.client.site.open_web_by_id(web.id).execute_query()
        self.assertIsNotNone(sub_site.id)

    # def test_10_get_site_links(self):
    #    result = self.client.site_linking_manager.get_site_links().execute_query()
    #    self.assertIsNotNone(result.value)

    def test_10_create_site(self):
        site_url = "{0}/sites/{1}".format(test_site_url, uuid.uuid4().hex)
        result = self.client.site_manager.create(
            "Comm Site", site_url, test_user_principal_name_alt
        ).execute_query()
        self.assertIsNotNone(result.value)
        self.__class__.site_response = result.value

    def test_11_get_site_status(self):
        site_url = self.__class__.site_response.SiteUrl
        result = self.client.site_manager.get_status(site_url).execute_query()
        self.assertIsNotNone(result.value.SiteStatus)
        self.assertTrue(result.value.SiteStatus != SiteStatus.Error)

    def test_12_get_site_url(self):
        site_id = self.__class__.site_response.SiteId
        result = self.client.site_manager.get_site_url(site_id).execute_query()
        self.assertIsNotNone(result.value)
        self.assertTrue(self.__class__.site_response.SiteUrl == result.value)

    def test_13_delete_site(self):
        from office365.sharepoint.client_context import ClientContext

        admin_ctx = ClientContext(self.client.base_url).with_credentials(
            test_admin_credentials
        )
        site_id = self.__class__.site_response.SiteId
        admin_ctx.site_manager.delete(site_id).execute_query()
