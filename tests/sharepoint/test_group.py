import uuid

from tests import test_user_principal_name
from tests.sharepoint.sharepoint_case import SPTestCase


class TestSharePointGroup(SPTestCase):
    target_group = None  # type: Group

    @classmethod
    def setUpClass(cls):
        super(TestSharePointGroup, cls).setUpClass()
        cls.target_user = cls.client.web.ensure_user(
            test_user_principal_name
        ).execute_query()

    def test1_create_group(self):
        grp_title = "Custom Group" + uuid.uuid4().hex
        result = self.client.web.site_groups.add(grp_title).execute_query()
        self.assertIsNotNone(result.resource_path)
        self.__class__.target_group = result

    def test2_add_user_to_group(self):
        target_user = self.__class__.target_group.users.add_user(
            self.target_user.login_name
        ).execute_query()
        self.assertIsNotNone(target_user.id)

    def test3_get_group_users(self):
        result = self.__class__.target_group.users.get().execute_query()
        self.assertGreaterEqual(len(result), 1)

    def test4_expand_to_principals(self):
        result = self.__class__.target_group.expand_to_principals().execute_query()
        self.assertIsNotNone(result.value)

    def test5_remove_user_from_group(self):
        result = self.__class__.target_group.users.remove_by_id(
            self.target_user.id
        ).execute_query()
        self.assertEqual(len(result), 0)

    def test6_delete_group(self):
        grp_id = self.__class__.target_group.id
        self.client.web.site_groups.remove_by_id(grp_id).execute_query()
