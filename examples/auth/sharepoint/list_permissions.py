from office365.graph_client import GraphClient
from tests import (
    test_client_id,
    test_client_secret,
    test_tenant,
)

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)

resource = client.service_principals.get_by_app_id(
    "00000003-0000-0ff1-ce00-000000000000"
)
# principal = client.service_principals.get_by_app_id(test_client_id).get().execute_query()
result = resource.get_application_permissions(test_client_id).execute_query()
for app_role in result.value:
    print(app_role)
