import uuid

from office365.directory.groupCreationProperties import GroupCreationProperties
from tests.graph_case import GraphTestCase


class TestGraphGroup(GraphTestCase):
    """Tests for Azure Active Directory (Azure AD) groups"""

    target_group = None

    def test1_create_group(self):
        grp_name = "Group_" + uuid.uuid4().hex
        properties = GroupCreationProperties(grp_name)
        new_group = self.client.groups.add(properties)
        self.client.execute_query()
        self.assertIsNotNone(new_group.properties['id'])
        self.__class__.target_group = new_group

    def test2_delete_group(self):
        grp_to_delete = self.__class__.target_group
        grp_to_delete.delete_object()
        self.client.execute_query()
