from examples import acquire_token_client_credentials
from office365.graph_client import GraphClient


client = GraphClient(acquire_token_client_credentials)
idp_col = client.identityProviders.get().execute_query()
for idp in idp_col:
    print(idp.id)
