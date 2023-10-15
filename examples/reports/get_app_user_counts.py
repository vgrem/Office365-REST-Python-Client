"""
Get a report that provides the trend in the number of active users for each app (Outlook, Word, Excel, PowerPoint,
OneNote, and Teams) in your organization.

https://learn.microsoft.com/en-us/graph/api/reportroot-getm365appusercounts?view=graph-rest-1.0
"""
import os
import tempfile

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient.with_client_secret(test_tenant, test_client_id, test_client_secret)
result = client.reports.get_m365_app_user_counts("D7").execute_query()
download_path = os.path.join(tempfile.mkdtemp(), "Report.csv")
with open(download_path, "wb") as f:
    f.write(result.value)
print("Report saved into : {0}".format(download_path))
