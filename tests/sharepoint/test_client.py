from unittest import TestCase

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.odata.type import ODataType
from office365.runtime.odata.query_options import QueryOptions
from office365.runtime.types.collections import StringCollection, GuidCollection
from office365.sharepoint.principal.users.id_info import UserIdInfo
from office365.sharepoint.tenant.administration.secondary_administrators_fields_data import \
    SecondaryAdministratorsFieldsData
from tests import test_site_url, test_client_credentials, test_user_credentials, settings, create_unique_name, \
    create_unique_file_name, test_team_site_url
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.sharepoint.client_context import ClientContext


class TestSharePointClient(TestCase):

    def test1_connect_with_app_principal(self):
        ctx = ClientContext(test_site_url).with_credentials(test_client_credentials)
        self.assertIsInstance(ctx.authentication_context._token_provider, ACSTokenProvider)

    def test2_connect_with_app_principal_alt(self):
        context_auth = AuthenticationContext(url=test_site_url)
        context_auth.acquire_token_for_app(client_id=settings.get('client_credentials', 'client_id'),
                                           client_secret=settings.get('client_credentials', 'client_secret'))
        ctx = ClientContext(test_site_url, context_auth)
        self.assertIsInstance(ctx.authentication_context._token_provider, ACSTokenProvider)

    def test4_connect_with_user_credentials(self):
        ctx = ClientContext(test_site_url).with_credentials(test_user_credentials)
        self.assertIsInstance(ctx.authentication_context._token_provider, SamlTokenProvider)

    def test5_init_from_url(self):
        page_url = "{site_url}/SitePages/Home.aspx".format(site_url=test_team_site_url)
        ctx = ClientContext.from_url(page_url).with_credentials(test_user_credentials)
        web = ctx.web.get().execute_query()
        self.assertIsNotNone(web.url)

    def test6_connect_with_client_cert(self):
        pass

    def test7_construct_get_request(self):
        pass

    def test8_execute_multiple_queries_sequentially(self):
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
        self.assertIsInstance(current_user.user_id, UserIdInfo)

    def test_10_execute_update_batch_request(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        web = client.web
        new_web_title = create_unique_name("Site")
        web.set_property("Title", new_web_title).update()
        client.execute_batch()

        updated_web = client.web.get().execute_query()
        self.assertEqual(updated_web.properties['Title'], new_web_title)

    def test_11_execute_get_and_update_batch_request(self):
        page_url = "/sites/team/SitePages/Home.aspx"
        client = ClientContext(test_team_site_url).with_credentials(test_user_credentials)
        list_item = client.web.get_file_by_server_relative_url(page_url).listItemAllFields
        new_title = create_unique_name("Page")
        list_item.set_property("Title", new_title).update()
        client.execute_batch()

        updated_list_item = client.web.get_file_by_server_relative_url(page_url).listItemAllFields.get().execute_query()
        self.assertEqual(updated_list_item.properties['Title'], new_title)

    def test_12_create_and_delete_batch_request(self):
        pass

    def test_13_get_and_delete_batch_request(self):
        file_name = create_unique_file_name("TestFile", "txt")
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        list_pages = client.web.lists.get_by_title("Documents")
        files = list_pages.root_folder.files.get().execute_query()
        files_count_before = len(files)
        new_file = list_pages.root_folder.upload_file(file_name, "-some content goes here-").execute_query()
        self.assertTrue(new_file.name, file_name)

        new_file.delete_object()
        files_after = list_pages.root_folder.files
        client.load(files_after)
        client.execute_batch()
        self.assertEqual(len(files_after), files_count_before)

    def test_14_get_entity_type_name(self):
        guid_coll = GuidCollection()
        self.assertEqual(guid_coll.entity_type_name, "Collection(Edm.Guid)")

        custom_type_name = ODataType.resolve_type(SecondaryAdministratorsFieldsData)
        self.assertEqual(custom_type_name,
                         "Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData")

        str_type_name = ODataType.resolve_type(StringCollection)
        self.assertEqual(str_type_name, "Collection(Edm.String)")

        str_col = StringCollection()
        self.assertEqual(str_col.entity_type_name, "Collection(Edm.String)")

        type_item = SecondaryAdministratorsFieldsData()
        self.assertEqual(type_item.entity_type_name,
                         "Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData")

        type_col = ClientValueCollection(SecondaryAdministratorsFieldsData)
        expected_type = "Collection(Microsoft.Online.SharePoint.TenantAdministration.SecondaryAdministratorsFieldsData)"
        self.assertEqual(type_col.entity_type_name, expected_type)

    def test_15_build_query_options(self):
        client = ClientContext(test_site_url)
        lib = client.web.default_document_library()
        options = QueryOptions.build(lib, ["Author", "Comments"])
        self.assertEqual(str(options), "$select=Author,Comments&$expand=Author")

    def test_16_ensure_property(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        me = client.web.current_user.get()
        site = client.site

        def _owner_loaded():
            self.assertIsNotNone(site.owner.id)
        site.ensure_property("Owner", _owner_loaded).get()
        lib = client.web.default_document_library().get()
        client.execute_query()
        self.assertIsNotNone(me.login_name)
        self.assertIsNotNone(lib.title)

    def test_17_test_client_result(self):
        client = ClientContext(test_site_url).with_credentials(test_user_credentials)
        result = ClientResult(client, StringCollection())
        self.assertIsInstance(result.value, StringCollection)

    def test_18_query_options_is_empty(self):
        options = QueryOptions()
        self.assertTrue(options.is_empty)
