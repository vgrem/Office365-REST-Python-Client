"""
Use the Microsoft Search API in Microsoft Graph to search content stored in OneDrive or SharePoint:
files, folders, lists, list items, or sites.
https://learn.microsoft.com/en-us/graph/search-concept-files
"""
import json

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
result = client.search.query_drive_items("Guide.docx").execute_query()
print(json.dumps(result.value.to_json(), indent=4))
