from tests import test_user_principal_name
from tests.graph_case import GraphTestCase


class TestRoleManagement(GraphTestCase):

    def test1_list_role_definitions(self):
        col = (
            self.client.role_management.directory.role_definitions.get().execute_query()
        )
        self.assertIsNotNone(col.resource_path)

    def test2_get_role_definition(self):
        result = (
            self.client.role_management.directory.role_definitions[
                "a0b1b346-4d3e-4e8b-98f8-753987be4970"
            ]
            .get()
            .execute_query()
        )
        self.assertIsNotNone(result.resource_path)

    def test3_list_role_assignments(self):
        col = (
            self.client.role_management.directory.role_assignments.get().execute_query()
        )
        self.assertIsNotNone(col.resource_path)

    def test4_get_user_role_assignments(self):
        user = (
            self.client.users.get_by_principal_name(test_user_principal_name)
            .get()
            .execute_query()
        )
        result = (
            self.client.role_management.directory.role_assignments.filter(
                "principalId eq '{0}'".format(user.id)
            )
            .get()
            .execute_query()
        )
        self.assertIsNotNone(result.resource_path)
