"""Tests for SharePoint user profile features including personal sites, people manager, and promoted links."""

from __future__ import annotations

from typing import ClassVar, Optional

from office365.runtime.client_request_exception import ClientRequestException
from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.userprofiles.my_site_links import MySiteLinks
from office365.sharepoint.userprofiles.people_manager import PeopleManager
from office365.sharepoint.webparts.tile_data import TileData

from tests import (
    test_client_id,
    test_password,
    test_team_site_url,
    test_tenant,
    test_user_principal_name,
    test_username,
)
from tests.sharepoint.sharepoint_case import SPTestCase


class TestUserProfile(SPTestCase):
    """Test SharePoint user profile features."""

    promoted_links: ClassVar[Optional[ClientValueCollection[TileData]]] = None

    @classmethod
    def setUpClass(cls):
        cls.my_client = ClientContext(test_team_site_url).with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )

    # def test1_get_owner_user_profile(self):
    #    from office365.sharepoint.userprofiles.profile_loader import ProfileLoader
    #    up = ProfileLoader.get_owner_user_profile(self.my_client).execute_query()
    #    self.assertIsNotNone(up.resource_path)

    def test_01_get_profile_loader(self):
        """Get the user profile loader."""
        user_profile = self.my_client.profile_loader.get_user_profile().execute_query()
        self.assertIsNotNone(user_profile.account_name)

    def test_02_create_personal_site(self):
        """Create a personal site for the current user."""
        user_profile = self.my_client.profile_loader.get_user_profile()
        up = user_profile.create_personal_site_enque(True).execute_query()
        self.assertIsNotNone(up.public_url)

    def test_03_get_user_props(self):
        """Get user profile properties for a target user."""
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        self.assertIsNotNone(target_user)
        self.assertIsNotNone(target_user.login_name)
        result = self.my_client.people_manager.get_user_profile_properties(target_user.login_name).execute_query()
        self.assertIsNotNone(result.value)

    def test_04_get_properties_for(self):
        """Get profile properties for the current user."""
        me = self.my_client.web.current_user
        properties = self.my_client.people_manager.get_properties_for(me).execute_query()
        self.assertIsNotNone(properties)

    def test_05_get_default_document_library(self):
        """Get the default document library for the current user."""
        me = self.my_client.web.current_user
        result = self.my_client.people_manager.get_default_document_library(me).execute_query()
        self.assertIsNotNone(result.value)

    def test_06_get_people_followed_by(self):
        """Get people followed by the current user."""
        me = self.my_client.web.current_user.get().execute_query()
        self.assertIsNotNone(me.login_name)
        result = self.my_client.people_manager.get_people_followed_by(me.login_name).execute_query()
        self.assertIsNotNone(result)

    def test_07_start_stop_following(self):
        """Follow and unfollow a user, observing the state flip.

        The endpoint takes the *claim* login name of a site user
        (``i:0#.f|membership|…``); a bare UPN has no people profile and is refused.
        The test leaves the tenant as it found it by choosing a user the caller does
        not already follow: following and then unfollowing a pre-existing
        relationship is not what this test is about.
        """
        people_manager = PeopleManager(self.my_client)
        target = self._find_unfollowed_user(people_manager)
        if target is None:
            self.skipTest("Every second site user is already followed or has no people profile")
        people_manager.follow(target).execute_query()
        self.assertTrue(people_manager.am_i_following(target).execute_query().value)
        people_manager.stop_following(target).execute_query()
        self.assertFalse(people_manager.am_i_following(target).execute_query().value)

    def _find_unfollowed_user(self, people_manager: PeopleManager) -> Optional[str]:
        """Returns the claim login name of a site user the caller does not follow."""
        my_login_name = self.my_client.web.current_user.get().execute_query().login_name
        for user in self.my_client.web.site_users.get().execute_query():
            login_name = user.login_name or ""
            if login_name == my_login_name or "|membership|" not in login_name:
                continue
            try:
                if not people_manager.am_i_following(login_name).execute_query().value:
                    return login_name
            except ClientRequestException:
                # A principal without a people profile cannot be followed at all.
                continue
        return None

    def test_08_get_followers_for(self):
        """Get followers for a target user."""
        target_user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
        self.assertIsNotNone(target_user)
        self.assertIsNotNone(target_user.login_name)
        col = self.my_client.people_manager.get_followers_for(target_user.login_name).execute_query()
        self.assertGreaterEqual(len(col), 0)

    def test_09_get_my_followers(self):
        """Get followers of the current user."""
        col = self.my_client.people_manager.get_my_followers().execute_query()
        self.assertGreaterEqual(len(col), 0)

    def test_10_get_trending_tags(self):
        """Get trending tags."""
        result = PeopleManager.get_trending_tags(self.my_client).execute_query()
        self.assertGreaterEqual(len(result.items), 0)

    def test_12_get_my_site_links(self):
        """Get My Site links."""
        result = MySiteLinks.get_my_site_links(self.my_client).execute_query()
        self.assertIsNotNone(result.all_documents_link)

    # def test_13_set_single_value_profile_property(self):
    #    user = self.my_client.web.ensure_user(test_user_principal_name).execute_query()
    #    self.my_client.people_manager.\
    #        set_single_value_profile_property(user.login_name, "Country", "Finland").execute_query()

    def test_13_add_site_link(self):
        """Add a promoted site link."""
        from office365.sharepoint.userprofiles.promoted_sites import PromotedSites

        PromotedSites.add_site_link(self.my_client, "https://www.google.com", "Google").execute_query()

    def test_14_get_promoted_links_as_tiles(self):
        """Get promoted links as tiles."""
        from office365.sharepoint.userprofiles.promoted_sites import PromotedSites

        result = PromotedSites.get_promoted_links_as_tiles(self.my_client).execute_query()
        self.assertIsNotNone(result.value)
        self.assertGreater(len(result.value), 0)
        TestUserProfile.promoted_links = result.value

    def test_15_delete_promoted_links(self):
        """Delete all promoted links."""
        from office365.sharepoint.userprofiles.promoted_sites import PromotedSites

        promoted_links = TestUserProfile.promoted_links
        if not promoted_links:
            self.skipTest("No promoted links from previous test")
        for promoted_link in promoted_links:
            self.assertIsNotNone(promoted_link.ID)
            PromotedSites.delete_site_link(self.my_client, promoted_link.ID)
        self.my_client.execute_batch()
        after_result = PromotedSites.get_promoted_links_as_tiles(self.my_client).execute_query()
        self.assertEqual(len(after_result.value), 0)

    # def test_17_shared_with_me(self):
    #    from office365.sharepoint.userprofiles.sharedwithme.items import SharedWithMeItems
    #    result = SharedWithMeItems.shared_with_me(self.my_client).execute_query()
    #    self.assertIsNotNone(result)
