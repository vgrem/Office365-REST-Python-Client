import uuid
from unittest import TestCase

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.portal.group_site_info import GroupSiteInfo
from office365.sharepoint.portal.group_site_manager import GroupSiteManager
from office365.sharepoint.portal.site_status import SiteStatus
from tests import test_site_url, test_user_credentials


class TestTeamSite(TestCase):
    site_info = None  # type: GroupSiteInfo

    @classmethod
    def setUpClass(cls):
        super(TestTeamSite, cls).setUpClass()
        cls.client = ClientContext(test_site_url).with_credentials(test_user_credentials)
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
