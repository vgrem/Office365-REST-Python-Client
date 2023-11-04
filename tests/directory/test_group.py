import unittest

from office365.directory.groups.group import Group
from office365.directory.users.user import User
from office365.runtime.client_request_exception import ClientRequestException
from tests import create_unique_name, test_user_principal_name
from tests.graph_case import GraphTestCase


class TestGraphGroup(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) groups"""

    target_group = None  # type: Group
    target_user = None  # type: User
    directory_quota_exceeded = False

    def test1_create_group(self):
        try:
            name = create_unique_name("Group")
            new_group = self.client.groups.create_m365(name).execute_query()
            self.assertIsNotNone(new_group.id)
            self.__class__.target_group = new_group
        except ClientRequestException as e:
            if e.code == "Directory_QuotaExceeded":
                self.directory_quota_exceeded = True
                result = self.client.me.get_member_groups().execute_query()
                self.assertIsNotNone(result.value)
                filter_expr = "displayName eq '{0}'".format(result.value[0])
                result = self.client.groups.filter(filter_expr).get().execute_query()
                self.__class__.target_group = result[0]

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test2_list_groups(self):
        groups = self.client.groups.top(1).get().execute_query()
        self.assertEqual(len(groups), 1)

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test3_get_group(self):
        existing_group = self.__class__.target_group
        target_group = self.client.groups[existing_group.id].get().execute_query()
        self.assertIsInstance(target_group, Group)

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test4_add_group_owner(self):
        users = (
            self.client.users.filter(
                "mail eq '{mail}'".format(mail=test_user_principal_name)
            )
            .get()
            .execute_query()
        )
        self.assertEqual(len(users), 1)

        owner_id = users[0].id
        grp = self.__class__.target_group
        grp.owners.add(owner_id).execute_query()
        self.__class__.target_user = users[0]

    def test5_list_group_owners(self):
        owners = self.__class__.target_group.owners.get().execute_query()
        self.assertGreater(len(owners), 0)

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test6_remove_group_owner(self):
        owner_id = self.__class__.target_user.id
        grp = self.__class__.target_group
        grp.owners.remove(owner_id).execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test7_add_group_member(self):
        member_id = self.__class__.target_user.id
        grp = self.__class__.target_group
        grp.members.add(member_id).execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test8_remove_group_member(self):
        member_id = self.__class__.target_user.id
        grp = self.__class__.target_group
        grp.members.remove(member_id).execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test9_delete_group(self):
        grp_to_delete = self.__class__.target_group
        grp_to_delete.delete_object(True).execute_query()

    def test_10_get_changes(self):
        changed_groups = (
            self.client.groups.delta.select(["displayName"]).get().execute_query()
        )
        self.assertGreater(len(changed_groups), 0)
