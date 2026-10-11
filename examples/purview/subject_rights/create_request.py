"""
Create a subject rights request (GDPR/CCPA data subject request).

Requires delegated permission ``SubjectRightsRequest.ReadWrite.All``.

https://learn.microsoft.com/en-us/graph/api/security-post-subjectrightsrequests
"""

from office365.graph_client import GraphClient
from office365.security.subjectrightsrequests.identity import SubjectRightsRequestIdentity
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

request = client.security.subject_rights_requests.add(
    type="export",
    displayName="GDPR Export Request — User Data",
    description="Data subject requested all personal data under GDPR Article 15.",
    internalDueDateTime="2026-07-05T00:00:00Z",
    dataSubject=SubjectRightsRequestIdentity(
        email="user@contoso.com",
    ),
).execute_query()

print(f"Request created: {request.properties.get('displayName')}")
print(f"  Type: {request.properties.get('type')}")
print(f"  Status: {request.properties.get('status')}")
