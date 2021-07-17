from office365.onedrive.site import Site
from tests.graph_case import GraphTestCase


class TestSite(GraphTestCase):
    """OneDrive specific test case base class"""
    target_site = None  # type: Site

    @classmethod
    def setUpClass(cls):
        super(TestSite, cls).setUpClass()
        cls.target_site = cls.client.sites.root
        cls.followed_sites_count = None
        assert cls.target_site.resource_path is not None

    @classmethod
    def tearDownClass(cls):
        pass

    def test1_get_root_site(self):
        root_site = self.target_site.get().execute_query()
        assert root_site.id is not None

    def test2_list_followed_sites(self):
        sites = self.client.me.followed_sites.get().execute_query()
        self.followed_sites_count = len(sites)

    def test3_follow(self):
        pass

    def test4_unfollow(self):
        pass
