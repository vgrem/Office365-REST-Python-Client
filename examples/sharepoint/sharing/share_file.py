import json

from office365.sharepoint.client_context import ClientContext
from office365.sharepoint.sharing.links.kind import SharingLinkKind
from office365.sharepoint.webs.web import Web
from tests import test_team_site_url, test_user_credentials

sharing_messages = {
    0: "A value has not been initialized",
    1: "A direct link or canonical URL to an object",
    2: "An organization access link with view permissions to an object",
    3: "An organization access link with edit permissions to an object",
    4: "An anonymous access link with view permissions to an object",
    5: "An anonymous access link with edit permissions to an object",
    6: "A tokenized sharing link where properties can change without affecting link URL",
}

ctx = ClientContext(test_team_site_url).with_credentials(test_user_credentials)

local_path = "../../data/SharePoint User Guide.docx"
lib = ctx.web.default_document_library()
with open(local_path, "rb") as f:
    remote_file = lib.root_folder.files.upload(f).execute_query()


print("Creating a sharing link for a file...")
result = remote_file.share_link(SharingLinkKind.AnonymousView).execute_query()
print(json.dumps(result.value.to_json(), indent=4))
link_url = result.value.sharingLinkInfo.Url

print("Verifying sharing link ...")
result = Web.get_sharing_link_kind(ctx, link_url).execute_query()
print(sharing_messages.get(result.value, "Unknown sharing link"))

print("Retrieving sharing link data ...")
result = ctx.web.get_sharing_link_data(link_url).execute_query()
print(json.dumps(result.value.to_json(), indent=4))

print("Unsharing a file link...")
remote_file.unshare_link(SharingLinkKind.AnonymousView).execute_query()

# Get file sharing info
info = remote_file.get_sharing_information().execute_query()
print("AnonymousViewLink:", info.properties.get("AnonymousViewLink"))
