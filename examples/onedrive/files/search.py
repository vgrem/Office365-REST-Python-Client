"""
Use the Microsoft Search API in Microsoft Graph to search content stored in OneDrive or SharePoint:
files, folders, lists, list items, or sites.
https://learn.microsoft.com/en-us/graph/search-concept-files
"""

from office365.graph_client import GraphClient
from tests.graph_case import acquire_token_by_username_password

client = GraphClient(acquire_token_by_username_password)
result = client.search.query_drive_items("Guide.docx").execute_query()
for item in result.value:
    for hit_container in item.hitsContainers:
        for hit in hit_container.hits:
            print(hit.resource)
