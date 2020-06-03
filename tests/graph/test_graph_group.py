import unittest
import uuid

from office365.graph.directory.group import Group
from office365.graph.directory.groupProfile import GroupProfile
from office365.graph.directory.user import User
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph.graph_case import GraphTestCase


class TestGraphGroup(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) groups"""

    target_group = None  # type: Group
    target_user = None   # type: User
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
            properties = GroupProfile(grp_name)
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
    def test3_get_group(self):
        existing_group = self.__class__.target_group
        group = self.client.groups[existing_group.id]
        self.client.execute_query()
        self.assertIsInstance(group, Group)

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not be created")
    def test4_add_group_owner(self):
        users = self.client.users.filter("mail eq 'mdoe@mediadev8.onmicrosoft.com'")
        self.client.load(users)
        self.client.execute_query()
        self.assertEqual(len(users), 1)

        owner_id = users[0].id
        grp = self.__class__.target_group
        grp.owners.add(owner_id)
        self.client.execute_query()
        self.__class__.target_user = users[0]

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test5_remove_group_owner(self):
        owner_id = self.__class__.target_user.id
        grp = self.__class__.target_group
        grp.owners.remove(owner_id)
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was created")
    def test6_add_group_member(self):
        member_id = self.__class__.target_user.properties["id"]
        grp = self.__class__.target_group
        grp.members.add(member_id)
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test7_remove_group_member(self):
        member_id = self.__class__.target_user.id
        grp = self.__class__.target_group
        grp.members.remove(member_id)
        self.client.execute_query()

    @unittest.skipIf(directory_quota_exceeded, "Skipping, group was not created")
    def test8_delete_group(self):
        grp_to_delete = self.__class__.target_group
        grp_to_delete.delete_object(True)
        self.client.execute_query()

