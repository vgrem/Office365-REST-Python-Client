import unittest
import uuid
from office365.graph.directory.groupCreationProperties import GroupCreationProperties
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph.graph_case import GraphTestCase


class TestGraphGroup(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) groups"""

    target_group = None
    target_user = None
    directory_quota_exceeded = False

    def test1_get_group_list(self):
        groups = self.client.groups.top(1)
        self.client.load(groups)
        self.client.execute_query()
        self.assertEqual(len(groups), 1)
        for group in groups:
            self.assertIsNotNone(group.properties['id'])

    def test2_create_group(self):
        try:
            grp_name = "Group_" + uuid.uuid4().hex
            properties = GroupCreationProperties(grp_name)
            properties.securityEnabled = False
            properties.mailEnabled = True
            properties.groupTypes = ["Unified"]
            new_group = self.client.groups.add(properties)
            self.client.execute_query()
            self.assertIsNotNone(new_group.properties['id'])
            self.__class__.target_group = new_group
        except ClientRequestException as e:
            if e.code == 'Directory_QuotaExceeded':
                self.directory_quota_exceeded = True
                result = self.client.me.get_member_groups()
                self.client.execute_query()
                if result.value:
                    self.assertIsNotNone(result.value)
                    result = self.client.groups.filter("displayName eq 'FirstDistGroup'".format(result.value[0]))
                    self.client.load(result)
                    self.client.execute_query()
                    self.__class__.target_group = result[0]

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test3_add_group_owner(self):
        users = self.client.users.filter("mail eq 'mdoe@mediadev8.onmicrosoft.com'")
        self.client.load(users)
        self.client.execute_query()
        self.assertEqual(len(users), 1)

        owner_id = users[0].properties["id"]
        grp = self.__class__.target_group
        grp.owners.add(owner_id)
        self.client.execute_query()
        self.__class__.target_user = users[0]

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test4_remove_group_owner(self):
        owner_id = self.__class__.target_user.properties["id"]
        grp = self.__class__.target_group
        grp.owners.remove(owner_id)
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test5_add_group_member(self):
        member_id = self.__class__.target_user.properties["id"]
        grp = self.__class__.target_group
        grp.members.add(member_id)
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test6_remove_group_member(self):
        member_id = self.__class__.target_user.properties["id"]
        grp = self.__class__.target_group
        grp.members.remove(member_id)
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test7_delete_group(self):
        grp_to_delete = self.__class__.target_group
        grp_to_delete.delete_object()
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test8_permanently_delete_group(self):
        deleted_groups = self.client.directory.deletedGroups
        self.client.load(deleted_groups)
        self.client.execute_query()
        count_before = len(deleted_groups)

        grp_to_delete = self.__class__.target_group
        deleted_group = self.client.directory.deletedGroups[grp_to_delete.id]
        deleted_group.delete_object()
        self.client.load(deleted_groups)
        self.client.execute_query()
        self.assertEqual(len(deleted_groups), count_before - 1)
