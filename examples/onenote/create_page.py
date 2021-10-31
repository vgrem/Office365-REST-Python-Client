from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

files = {}
with open("../data/Sample.html", 'rb') as f, \
    open("../data/Office_365_logo.png", 'rb') as img_f, \
    open("../data/Sample.pdf", 'rb') as pdf_f:
    presentation_file = f
    files["imageBlock1"] = img_f
    files["fileBlock1"] = pdf_f
    page = client.me.onenote.pages.add(presentation_file=presentation_file, attachment_files=files).execute_query()
print(page.title)
