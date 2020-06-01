import uuid
from unittest import TestCase
from office365.runtime.auth.authentication_context import AuthenticationContext
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.GroupSiteManager import GroupSiteManager
from office365.sharepoint.portal.SiteStatus import SiteStatus
from settings import settings


class TestTeamSite(TestCase):
    site_info = None

    @classmethod
    def setUpClass(cls):
        super(TestTeamSite, cls).setUpClass()
        ctx_auth = AuthenticationContext(url=settings['url'])
        ctx_auth.acquire_token_for_user(username=settings['user_credentials']['username'],
                                        password=settings['user_credentials']['password'])
        cls.client = ClientContext(settings['url'], ctx_auth)
        cls.site_manager = GroupSiteManager(cls.client)

    def test1_create_site(self):
        pass
        #site_name = "TeamSite{0}".format(uuid.uuid4().hex)
        #info = self.site_manager.create_group_ex("Team Site", site_name, True, None)
        #self.client.execute_query()
        #self.assertIsNotNone(info.GroupId)
        #self.__class__.site_info = info

    def test2_get_site_status(self):
        pass
        #info = self.site_manager.get_status(self.__class__.site_info.GroupId)
        #self.client.execute_query()
        #self.assertIsNotNone(info.SiteStatus)
        #self.assertTrue(info.SiteStatus == SiteStatus.Ready)

    def test3_delete_site(self):
        pass
        #self.site_manager.delete(self.__class__.site_info.SiteUrl)
        #self.client.execute_query()
