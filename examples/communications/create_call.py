"""
Create peer-to-peer VoIP call with service hosted media
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
call = client.communications.calls.create(
    "https://mediadev8.com/teamsapp/api/calling"
).execute_query()
