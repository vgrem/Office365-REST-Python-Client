"""
Create OneNote pages

https://learn.microsoft.com/en-us/graph/onenote-create-page
"""

from office365.graph_client import GraphClient
from tests import test_client_id, test_password, test_tenant, test_username

client = GraphClient.with_username_and_password(
    test_tenant, test_client_id, test_username, test_password
)

files = {}
with open("../data/Sample.html", "rb") as f, open(
    "../data/office-logo-icon.jpg", "rb"
) as img_f, open("../data/Sample.pdf", "rb") as pdf_f, open(
    "../data/SharePoint User Guide.docx", "rb"
) as word_f:
    files["imageBlock1"] = img_f
    files["fileBlock1"] = pdf_f
    files["fileBlock2"] = word_f
    page = client.me.onenote.pages.add(
        presentation_file=f, attachment_files=files
    ).execute_query()
print(page.links.oneNoteWebUrl)
