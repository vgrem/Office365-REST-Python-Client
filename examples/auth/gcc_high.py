"""
Connect via national clouds (Microsoft 365 GCC High environment)

Microsoft Graph for US Government L4: https://graph.microsoft.us
"""

from office365.azure_env import AzureEnvironment
from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
    test_user_principal_name,
)

client = GraphClient(
    tenant=test_tenant, environment=AzureEnvironment.USGovernmentHigh
).with_client_secret(test_client_id, test_client_secret)
messages = client.users[test_user_principal_name].messages.get().execute_query()
