"""
Run an advanced hunting KQL query against Microsoft 365 Defender data.

Queries tables such as AlertInfo, DeviceProcessEvents, EmailEvents,
IdentityLogonEvents, and more.

This example finds sign-in attempts from outside the tenant domain
in the last 7 days.

Requires delegated permission ``ThreatHunting.Read.All``.

https://learn.microsoft.com/en-us/graph/api/security-security-runhuntingquery
"""

from office365.graph_client import GraphClient
from tests.settings import client_id, client_secret, tenant

client = GraphClient(tenant=tenant).with_client_secret(client_id, client_secret)

query = """
AADSignInEventsBeta
| where Timestamp > ago(7d)
| where isnotempty(IncomingTokenType)
| where CountryCode != "US"
| project Timestamp, AccountUpn, AppDisplayName, ClientAppUsed, CountryCode
| take 20
"""

result = client.security.run_hunting_query(query).execute_query()
for row in result.value:
    print(f"  {row}")
