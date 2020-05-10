import uuid
from unittest import TestCase

from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.SPSiteCreationRequest import SPSiteCreationRequest
from office365.sharepoint.portal.SPSiteManager import SPSiteManager
from office365.sharepoint.portal.SiteStatus import SiteStatus
from settings import settings



def load_current_user(ctx):
    current_user = ctx.web.currentUser
    ctx.load(current_user)
    ctx.execute_query()
    return current_user


class TestCommunicationSite(TestCase):
    site_response = None

    @classmethod
    def setUpClass(cls):
        super(TestCommunicationSite, cls).setUpClass()
        ctx_auth = AuthenticationContext(url=settings['url'])
        ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                        password=settings['user_credentials']['password'])
        cls.client = ClientContext(settings['url'], ctx_auth)
        cls.site_manager = SPSiteManager(cls.client)

    def test1_create_site(self):
        current_user = load_current_user(self.client)
        site_url = "{0}sites/{1}".format(settings["url"], uuid.uuid4().hex)
        request = SPSiteCreationRequest("CommSite123", site_url, current_user.properties['UserPrincipalName'])
        response = self.site_manager.create(request)
        self.client.execute_query()
        self.assertIsNotNone(response.SiteStatus)
        self.__class__.site_response = response

    def test2_get_site_status(self):
        response = self.site_manager.get_status(self.__class__.site_response.SiteUrl)
        self.client.execute_query()
        self.assertIsNotNone(response.SiteStatus)
        self.assertTrue(response.SiteStatus != SiteStatus.Error)

    def test3_delete_site(self):
        self.site_manager.delete(self.__class__.site_response.SiteId)
        self.client.execute_query()
