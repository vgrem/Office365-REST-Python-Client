from unittest import TestCase

from settings import settings
from tests import random_seed

from office365.runtime.auth.client_credential import ClientCredential
from office365.runtime.auth.providers.acs_token_provider import ACSTokenProvider
from office365.runtime.auth.providers.saml_token_provider import SamlTokenProvider
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

user_credentials = UserCredential(settings.get('user_credentials').get('username'),
                                  settings.get('user_credentials').get('password'))


class TestSharePointClient(TestCase):

    def test1_connect_with_app_principal(self):
        credentials = ClientCredential(settings.get('client_credentials').get('client_id'),
                                       settings.get('client_credentials').get('client_secret'))
        ctx = ClientContext.connect_with_credentials(settings['url'], credentials)
        self.assertIsInstance(ctx.authentication_context.provider, ACSTokenProvider)
        self.assertIsInstance(ctx.authentication_context.provider.token, TokenResponse)
        self.assertTrue(ctx.authentication_context.provider.token.is_valid)

    def test2_connect_with_user_credentials(self):
        ctx = ClientContext.connect_with_credentials(settings['url'], user_credentials)
        self.assertIsInstance(ctx.authentication_context.provider, SamlTokenProvider)

    def test3_init_from_url(self):
        ctx = ClientContext.from_url(settings['url']).with_credentials(user_credentials)
        web = ctx.web.load().execute_query()
        self.assertIsNotNone(web.url)

    def test4_connect_with_client_cert(self):
        pass

    def test5_get_batch_request(self):
        client = ClientContext(settings['url']).with_credentials(user_credentials)
        current_user = client.web.currentUser
        client.load(current_user)
        current_web = client.web
        client.load(current_web)
        client.execute_batch()
        self.assertIsNotNone(current_web.url)
        self.assertIsNotNone(current_user.user_id)

    def test6_update_batch_request(self):
        client = ClientContext(settings['url']).with_credentials(user_credentials)
        web = client.web
        new_web_title = "Site %s" % random_seed
        web.set_property("Title", new_web_title)
        web.update()
        client.execute_batch()

        updated_web = client.web
        client.load(updated_web)
        client.execute_query()
        self.assertEqual(updated_web.properties['Title'], new_web_title)

    def test7_get_and_update_batch_request(self):
        client = ClientContext(settings['url']).with_credentials(user_credentials)
        list_item = client.web.get_file_by_server_relative_url("/SitePages/Home.aspx").listItemAllFields
        new_title = "Page %s" % random_seed
        list_item.set_property("Title", new_title)
        list_item.update()
        client.execute_batch()

        updated_list_item = client.web.get_file_by_server_relative_url("/SitePages/Home.aspx").listItemAllFields
        client.load(updated_list_item)
        client.execute_query()
        self.assertEqual(updated_list_item.properties['Title'], new_title)

    def test8_create_and_delete_batch_request(self):
        pass

    def test9_get_and_delete_batch_request(self):
        file_name = "TestFile{0}.txt".format(random_seed)
        client = ClientContext(settings['url']).with_credentials(user_credentials)
        list_pages = client.web.lists.get_by_title("Documents")
        files = list_pages.rootFolder.files
        client.load(files)
        client.execute_query()
        files_count_before = len(files)
        new_file = list_pages.rootFolder.upload_file(file_name, "-some content goes here-")
        client.execute_query()
        self.assertTrue(new_file.name, file_name)

        new_file.delete_object()
        files_after = list_pages.rootFolder.files
        client.load(files_after)
        client.execute_batch()
        self.assertTrue(len(files_after), files_count_before)
