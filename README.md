# About
Office 365 & Microsoft Graph library for Python

# Usage

1. [Installation](#Installation)
2. [Working with SharePoint API](#Working-with-SharePoint-API) 
3. [Working with Outlook API](#Working-with-Outlook-API) 
4. [Working with OneDrive API](#Working-with-OneDrive-API)
5. [Working with Teams API](#Working-with-Microsoft-Teams-API)
6. [Working with OneNote API](#Working-with-Microsoft-OneNote-API)
7. [Working with Planner API](#Working-with-Microsoft-Planner-API)  

## Status
[![Downloads](https://pepy.tech/badge/office365-rest-python-client/month)](https://pepy.tech/project/office365-rest-python-client)
[![PyPI](https://img.shields.io/pypi/v/Office365-REST-Python-Client.svg)](https://pypi.python.org/pypi/Office365-REST-Python-Client)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/Office365-REST-Python-Client.svg)](https://pypi.python.org/pypi/Office365-REST-Python-Client/)
[![Build Status](https://travis-ci.com/vgrem/Office365-REST-Python-Client.svg?branch=master)](https://travis-ci.com/vgrem/Office365-REST-Python-Client)

# Installation

Use pip:

```
pip install Office365-REST-Python-Client
```

### Note 
>

>Alternatively the _latest_ version could be directly installed via GitHub:
>```
>pip install git+https://github.com/vgrem/Office365-REST-Python-Client.git
>```


# Working with SharePoint API

The list of supported API versions: 
-   [SharePoint 2013 REST API](https://msdn.microsoft.com/en-us/library/office/jj860569.aspx) and above 
-   SharePoint Online & OneDrive for Business REST API

#### Authentication

The following auth flows are supported:

- app principals flow: 
  `ClientContext.with_credentials(client_credentials)`
  
  Usage:
  ``` 
  client_credentials = ClientCredential('{client_id}','{client_secret}')
  ctx = ClientContext('{url}').with_credentials(client_credentials)
  ```
  Documentation: refer [Granting access using SharePoint App-Only](https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs) for a details  
  
  Example: [connect_with_app_principal.py](examples/sharepoint/connect_with_app_only_principal.py)
  
- user credentials flow: `ClientContext.with_credentials(user_credentials)`

  Usage:
  ``` 
  user_credentials = UserCredential('{username}','{password}')
  ctx = ClientContext('{url}').with_credentials(user_credentials)
  ```
  Example: [connect_with_user_credential.py](examples/sharepoint/connect_with_user_credential.py)
  
- certificate credentials flow: `ClientContext.with_certificate(tenant, client_id, thumbprint, cert_path)`

  Documentation: [Granting access via Azure AD App-Only](https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azuread)  
  
  Example: [connect_with_client_certificate.py](examples/sharepoint/connect_with_client_certificate.py)

#### Examples
 
There are **two approaches** available to perform API queries:

1. `ClientContext class` - where you target SharePoint resources such as `Web`, `ListItem` and etc (recommended)
 
```python
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
site_url = "https://{your-tenant-prefix}.sharepoint.com"
ctx = ClientContext(site_url).with_credentials(UserCredential("{username}", "{password}"))
web = ctx.web
ctx.load(web)
ctx.execute_query()
print("Web title: {0}".format(web.properties['Title']))
```
or alternatively via method chaining (a.k.a Fluent Interface): 

```python
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext
site_url = "https://{your-tenant-prefix}.sharepoint.com"
ctx = ClientContext(site_url).with_credentials(UserCredential("{username}", "{password}"))
web = ctx.web.get().execute_query()
print("Web title: {0}".format(web.properties['Title']))
```


2. `RequestOptions class` - where you construct REST queries (and no model is involved)

   The example demonstrates how to read `Web` properties:
   
```python
import json
from office365.runtime.auth.user_credential import UserCredential
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext
site_url = "https://{your-tenant-prefix}.sharepoint.com"
ctx = ClientContext(site_url).with_credentials(UserCredential("{username}", "{password}"))
request = RequestOptions("{0}/_api/web/".format(site_url))
response = ctx.pending_request().execute_request_direct(request)
json = json.loads(response.content)
web_title = json['d']['Title']
print("Web title: {0}".format(web_title))
```


The list of examples:

- Working with files
  - [download a file](examples/sharepoint/files/download_file.py) 
  - [upload a file](examples/sharepoint/files/upload_file.py)

- Working with lists and list items
  -  [create a list item](examples/sharepoint/lists/data_generator.py)
  -  [read a list item](examples/sharepoint/lists/read_large_list.py)   
  -  [update a list item](examples/sharepoint/listitems/update_items_batch.py)
  -  [delete a list item](examples/sharepoint/listitems/delete_list_item.py) 
  
Refer [examples section](examples/sharepoint) for another scenarios

# Working with Outlook API

The list of supported APIs:
-   [Outlook Contacts REST API](https://msdn.microsoft.com/en-us/office/office365/api/contacts-rest-operations)
-   [Outlook Calendar REST API](https://msdn.microsoft.com/en-us/office/office365/api/calendar-rest-operations)
-   [Outlook Mail REST API](https://msdn.microsoft.com/en-us/office/office365/api/mail-rest-operations)


Since Outlook REST APIs are available in both Microsoft Graph and the Outlook API endpoint, 
the following clients are available:

- `GraphClient` which targets Outlook API `v2.0` version (*preferable* nowadays, refer [transition to Microsoft Graph-based Outlook REST API](https://docs.microsoft.com/en-us/outlook/rest/compare-graph-outlook) for a details)   
~~- `OutlookClient` which targets Outlook API `v1.0` version (not recommended for usage since `v1.0` version is being deprecated.)~~


#### Authentication

[The Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/) which comes as a dependency 
is used as a default library to obtain tokens to call Microsoft Graph API. 

Using [Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/)

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)
> in the provided examples

```python
import msal
from office365.graph_client import GraphClient

def acquire_token():
    """
    Acquire token via MSAL
    """
    authority_url = 'https://login.microsoftonline.com/{tenant_id_or_name}'
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id='{client_id}',
        client_credential='{client_secret}'
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token


client = GraphClient(acquire_token)

```

But in terms of Microsoft Graph API authentication, another OAuth spec compliant libraries 
such as [adal](https://github.com/AzureAD/azure-activedirectory-library-for-python) 
are supported as well.   

Using [ADAL Python](https://adal-python.readthedocs.io/en/latest/#)

Usage

```python
import adal
from office365.graph_client import GraphClient

def acquire_token_func():
    authority_url = 'https://login.microsoftonline.com/{tenant_id_or_name}'
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        "{client_id}",
        "{client_secret}")
    return token

client = GraphClient(acquire_token_func)

```

#### Example

The example demonstrates how to send an email via [Microsoft Graph endpoint](https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0&tabs=http).

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)

```python
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_func)

client.me.send_mail(
    subject="Meet for lunch?",
    body="The new cafeteria is open.",
    to_recipients=["fannyd@contoso.onmicrosoft.com"]
).execute_query()

```


# Working with OneDrive API

#### Documentation 

[OneDrive Graph API reference](https://docs.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0)

#### Authentication

[The Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/) which comes as a dependency 
is used to obtain token

```python
import msal

def acquire_token_func():
    """
    Acquire token via MSAL
    """
    authority_url = 'https://login.microsoftonline.com/{tenant_id_or_name}'
    app = msal.ConfidentialClientApplication(
        authority=authority_url,
        client_id='{client_id}',
        client_credential='{client_secret}'
    )
    token = app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])
    return token
``` 


#### Examples 

##### Example: list available drives

The example demonstrates how to enumerate and print drive's url 
which corresponds to [`list available drives` endpoint](https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/drive_list?view=odsp-graph-online)

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)

```python
from office365.graph_client import GraphClient

tenant_name = "contoso.onmicrosoft.com"
client = GraphClient(acquire_token_func)
drives = client.drives.get().execute_query()
for drive in drives:
    print("Drive url: {0}".format(drive.web_url))
```


##### Example: download the contents of a DriveItem(folder facet)

```python
from office365.graph_client import GraphClient
client = GraphClient(acquire_token_func)
# retrieve drive properties 
drive = client.users["{user_id_or_principal_name}"].drive.get().execute_query()
# download files from OneDrive into local folder 
with tempfile.TemporaryDirectory() as path:
    download_files(drive.root, path)
```

where

```python
def download_files(remote_folder, local_path):
    drive_items = remote_folder.children.get().execute_query()
    for drive_item in drive_items:
        if drive_item.file is not None:  # is file?
            # download file content
            with open(os.path.join(local_path, drive_item.name), 'wb') as local_file:
                drive_item.download(local_file).execute_query()
```


Refer [OneDrive examples section](examples/onedrive) for a more examples.


# Working with Microsoft Teams API

#### Authentication

[The Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/) which comes as a dependency 
is used to obtain token  

#### Examples 

##### Example: create a new team under a group

The example demonstrates how create a new team under a group 
which corresponds to [`Create team` endpoint](https://docs.microsoft.com/en-us/graph/api/team-put-teams?view=graph-rest-1.0&tabs=http)

```python
from office365.graph_client import GraphClient
client = GraphClient(acquire_token_func)
new_team = client.groups["{group_id}"].add_team().execute_query_retry()
```

# Working with Microsoft Onenote API

The library supports OneNote API in terms of calls to a user's OneNote notebooks, sections, and pages in a personal or organization account

Example: Create a new page

```python
from office365.graph_client import GraphClient
client = GraphClient(acquire_token_func)

files = {}
with open("./MyPage.html", 'rb') as f, \
    open("./MyImage.png", 'rb') as img_f, \
    open("./MyDoc.pdf", 'rb') as pdf_f:
    files["imageBlock1"] = img_f
    files["fileBlock1"] = pdf_f
    page = client.me.onenote.pages.add(presentation_file=f, attachment_files=files).execute_query()
```

# Working with Microsoft Planner API

The example demonstrates how to create a new planner task
which corresponds to [`Create plannerTask` endpoint](https://docs.microsoft.com/en-us/graph/api/planner-post-tasks?view=graph-rest-1.0):

```python
from office365.graph_client import GraphClient

client = GraphClient(acquire_token_func)
task = client.planner.tasks.add(title="New task", planId="--plan id goes here--").execute_query()
```

# Third Party Libraries and Dependencies
The following libraries will be installed when you install the client library:
* [requests](https://github.com/kennethreitz/requests)
* [Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/)



