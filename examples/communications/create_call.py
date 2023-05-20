"""
Create peer-to-peer VoIP call with service hosted media
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_client_credentials

client = GraphClient(acquire_token_by_client_credentials)
call = client.communications.calls.create("https://mediadev8.com/teamsapp/api/calling").execute_query()
