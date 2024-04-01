from unittest import TestCase

from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_password,
    test_tenant,
    test_username,
)


class GraphTestCase(TestCase):
    """Microsoft Graph specific test case base class"""

    client = None  # type: GraphClient

    @classmethod
    def setUpClass(cls):
        cls.client = GraphClient.with_username_and_password(
            test_tenant, test_client_id, test_username, test_password
        )
