from examples import acquire_token_by_username_password
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_by_username_password)

files = {}
with open("../data/Sample.html", 'rb') as f, \
    open("../data/office-logo-icon.jpg", 'rb') as img_f, \
    open("../data/Sample.pdf", 'rb') as pdf_f, \
    open("../data/SharePoint User Guide.docx", 'rb') as word_f:
    files["imageBlock1"] = img_f
    files["fileBlock1"] = pdf_f
    files["fileBlock2"] = word_f
    page = client.me.onenote.pages.add(presentation_file=f, attachment_files=files).execute_query()
print(page.links.oneNoteWebUrl)
