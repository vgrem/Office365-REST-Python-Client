import uuid
from office365.directory.groupCreationProperties import GroupCreationProperties
from office365.runtime.client_request_exception import ClientRequestException
from tests.graph_case import GraphTestCase


class TestGraphGroup(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) groups"""

    target_group = None

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
                self.__class__.target_group = None
            else:
                raise

    def test3_delete_group(self):
        grp_to_delete = self.__class__.target_group
        if grp_to_delete is not None:
            grp_to_delete.delete_object()
            self.client.execute_query()

