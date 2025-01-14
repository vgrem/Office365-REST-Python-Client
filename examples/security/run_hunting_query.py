"""
This example specifies a KQL query which does the following:

   - Looks into the DeviceProcessEvents table in the advanced hunting schema.
   - Filters on the condition that the event is initiated by the powershell.exe process.
   - Specifies the output of 3 columns from the same table for each row: Timestamp, FileName, InitiatingProcessFileName.
   - Sorts the output by the Timestamp value.
   - Limits the output to 2 records (2 rows)

"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)
query = """
DeviceProcessEvents | where InitiatingProcessFileName =~ \"powershell.exe\" | project Timestamp, FileName, \
InitiatingProcessFileName | order by Timestamp desc | limit 2"""
result = client.security.run_hunting_query(query).execute_query()
print(result.value)
