"""
Create an activity

https://learn.microsoft.com/en-us/graph/api/projectrome-put-activity?view=graph-rest-1.0
"""
from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
