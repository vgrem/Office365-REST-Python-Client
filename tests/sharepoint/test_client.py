from unittest import TestCase

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import \
    SecondaryAdministratorsFieldsData
from tests import random_seed, test_site_url, test_client_credentials, test_user_credentials, settings
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext


class TestSharePointClient(TestCase):

    def test1_connect_with_app_principal(self):
        ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
        self.assertIsInstance(ctx.authentication_context._provider, ACSTokenProvider)

    def test2_connect_with_app_principal_alt(self):
        context_auth = AuthenticationContext(url=test_site_url)
        context_auth.acquire_token_for_app(client_id=settings.get('client_credentials', 'client_id'),
                                           client_secret=settings.get('client_credentials', 'client_secret'))
        ctx = ClientContext(test_site_url, context_auth)
        self.assertIsInstance(ctx.authentication_context._provider, ACSTokenProvider)

    def test4_connect_with_user_credentials(self):
        ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
        self.assertIsInstance(ctx.authentication_context._provider, SamlTokenProvider)

    def test5_init_from_url(self):
        ctx = ClientContext.from_url(test_site_url).with_credentials(test_user_credentials)
        web = ctx.web.get().execute_query()
        self.assertIsNotNone(web.url)

    def test6_connect_with_client_cert(self):
        pass

    def test7_construct_get_request(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        request = client.web.current_user.get().build_request()
        self.assertIsInstance(request, RequestOptions)

    def test8_execute_multiple_queries(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        current_user = client.web.current_user
        client.load(current_user)
        current_web = client.web
        client.load(current_web)
        client.execute_query()
        self.assertIsNotNone(current_web.url)
        self.assertIsNotNone(current_user.user_id)

    def test9_execute_get_batch_request(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        current_user = client.web.current_user
        client.load(current_user)
        current_web = client.web
        client.load(current_web)
        client.execute_batch()
        self.assertIsNotNone(current_web.url)
        self.assertIsNotNone(current_user.user_id)

    def test_10_execute_update_batch_request(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        web = client.web
        new_web_title = "Site %s" % random_seed
        web.set_property("Title", new_web_title)
        web.update()
        client.execute_batch()

        updated_web = client.web
        client.load(updated_web)
        client.execute_query()
        self.assertEqual(updated_web.properties['Title'], new_web_title)

    def test_11_execute_get_and_update_batch_request(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        list_item = client.web.get_file_by_server_relative_url("/SitePages/Home.aspx").listItemAllFields
        new_title = "Page %s" % random_seed
        list_item.set_property("Title", new_title)
        list_item.update()
        client.execute_batch()

        updated_list_item = client.web.get_file_by_server_relative_url("/SitePages/Home.aspx").listItemAllFields
        client.load(updated_list_item)
        client.execute_query()
        self.assertEqual(updated_list_item.properties['Title'], new_title)

    def test_12_create_and_delete_batch_request(self):
        pass

    def test_13_get_and_delete_batch_request(self):
        file_name = "TestFile{0}.txt".format(random_seed)
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        list_pages = client.web.lists.get_by_title("Documents")
        files = list_pages.root_folder.files
        client.load(files)
        client.execute_query()
        files_count_before = len(files)
        new_file = list_pages.root_folder.upload_file(file_name, "-some content goes here-")
        client.execute_query()
        self.assertTrue(new_file.name, file_name)

        new_file.delete_object()
        files_after = list_pages.root_folder.files
        client.load(files_after)
        client.execute_batch()
        self.assertTrue(len(files_after), files_count_before)

    def test_14_get_entity_type_name(self):
        str_col = ClientValueCollection(str, [])
        self.assertEqual(str_col.entity_type_name, "Collection(Edm.String)")

        self.assertEqual(SecondaryAdministratorsFieldsData._entity_type_name,
                         "Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData")

        type_item = SecondaryAdministratorsFieldsData(None, [])
        self.assertEqual(type_item.entity_type_name,
                         "Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData")

        type_col = ClientValueCollection(SecondaryAdministratorsFieldsData)
        expected_type = "Collection(Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData)"
        self.assertEqual(type_col.entity_type_name, expected_type)
