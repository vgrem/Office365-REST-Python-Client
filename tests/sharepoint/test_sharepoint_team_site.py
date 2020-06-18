import uuid
from unittest import TestCase
from office365.runtime.auth.userCredential import UserCredential
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.GroupSiteInfo import GroupSiteInfo
from office365.sharepoint.portal.GroupSiteManager import GroupSiteManager
from office365.sharepoint.portal.SiteStatus import SiteStatus
from settings import settings


class TestTeamSite(TestCase):
    site_info = None  # type: GroupSiteInfo

    @classmethod
    def setUpClass(cls):
        super(TestTeamSite, cls).setUpClass()

        user_credentials = UserCredential(settings['user_credentials']['username'],
                                          settings['user_credentials']['password'])
        cls.client = ClientContext(settings['url']).with_credentials(user_credentials)
        cls.site_manager = GroupSiteManager(cls.client)

    def test1_create_site(self):
        site_name = "TeamSite{0}".format(uuid.uuid4().hex)
        info = self.site_manager.create_group_ex("Team Site", site_name, True, None)
        self.client.execute_query()
        self.assertIsNotNone(info.GroupId)
        self.__class__.site_info = info

    def test2_get_site_status(self):
        info = self.site_manager.get_status(self.__class__.site_info.GroupId)
        self.client.execute_query()
        self.assertIsNotNone(info.SiteStatus)
        self.assertTrue(info.SiteStatus == SiteStatus.Ready)

    def test3_delete_site(self):
        self.site_manager.delete(self.__class__.site_info.SiteUrl)
        self.client.execute_query()
