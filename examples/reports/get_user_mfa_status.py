from office365.graph_client import GraphClient
from tests import test_client_id, test_client_secret, test_tenant

client = GraphClient(tenant=test_tenant).with_client_secret(
    test_client_id, test_client_secret
)

result = (
    client.reports.authentication_methods.user_registration_details.get().execute_query()
)
for details in result:
    print("{0}: {1}".format(details.user_principal_name, details.is_mfa_registered))
