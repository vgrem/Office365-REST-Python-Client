from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient


client = GraphClient(acquire_token_by_username_password)

with open("../data/Sample.html", 'rb') as f:
    html_content = f.read()

page = client.me.onenote.pages.add(presentation={"name": f.name, "content": html_content}).execute_query()
print(page.title)
