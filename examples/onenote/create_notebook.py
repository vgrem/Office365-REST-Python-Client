from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient
from tests import create_unique_name

client = GraphClient(acquire_token_by_username_password)

display_name = create_unique_name("My Private notebook")
notebook = client.me.onenote.notebooks.add(display_name).execute_query()
print(notebook.display_name)

