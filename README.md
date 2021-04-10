# About
Office 365 & Microsoft Graph library for Python

# Usage

1.   [Installation](#Installation)
1.   [Working with SharePoint API](#Working-with-SharePoint-API) 
2.   [Working with Outlook API](#Working-with-Outlook-API) 
3.   [Working with OneDrive API](#Working-with-OneDrive-API)
4.   [Working with Microsoft Teams API](#Working-with-Microsoft-Teams-API)    


## Status
[![Downloads](https://pepy.tech/badge/office365-rest-python-client/month)](https://pepy.tech/project/office365-rest-python-client)
[![PyPI](https://img.shields.io/pypi/v/Office365-REST-Python-Client.svg)](https://pypi.python.org/pypi/Office365-REST-Python-Client)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/Office365-REST-Python-Client.svg)](https://pypi.python.org/pypi/Office365-REST-Python-Client/)
[![Build Status](https://travis-ci.org/vgrem/Office365-REST-Python-Client.svg?branch=master)](https://travis-ci.org/vgrem/Office365-REST-Python-Client)

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
  client_credentials = ClientCredential('{client_id}'),'{client_secret}')
  ctx = ClientContext('{url}').with_credentials(client_credentials)
  ```
  Documentation: refer [Granting access using SharePoint App-Only](https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs) for a details  
  
  Example: [connect_with_app_principal.py](examples/sharepoint/connect_with_app_principal.py)
  
- user credentials flow: `ClientContext.with_credentials(user_credentials)`

  Usage:
  ``` 
  user_credentials = UserCredential('{username}'),'{password}')
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
response = ctx.execute_request_direct(request)
json = json.loads(response.content)
web_title = json['d']['Title']
print("Web title: {0}".format(web_title))
```


The list of examples:

- Working with files
  - [download a file](examples/sharepoint/files/download_file.py) 
  - [upload a file](examples/sharepoint/files/upload_file.py)

- Working with lists and list items
  -  [create a list item](examples/sharepoint/lists_and_items/data_generator.py)
  -  [read a list item](examples/sharepoint/lists_and_items/read_large_list.py)   
  -  [update a list item](examples/sharepoint/lists_and_items/update_items_batch.py)
  -  delete a list item 
  

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

But in terms of Microsoft Graph API authentication, another Microsoft Authentication Client compliant libraries 
such as [adal](https://github.com/AzureAD/azure-activedirectory-library-for-python) 
are supported as well.   

Using [ADAL Python](https://adal-python.readthedocs.io/en/latest/#)

Usage

```python
import adal
from office365.graph_client import GraphClient

def acquire_token():
    authority_url = 'https://login.microsoftonline.com/{tenant_id_or_name}'
    auth_ctx = adal.AuthenticationContext(authority_url)
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        "{client_id}",
        "{client_secret}")
    return token

client = GraphClient(acquire_token)

```

#### Example

The example demonstrates how to send an email via [Microsoft Graph endpoint](https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0&tabs=http).

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)

```python
from office365.graph_client import GraphClient

client = GraphClient(acquire_token)

message_json = {
    "Message": {
        "Subject": "Meet for lunch?",
        "Body": {
            "ContentType": "Text",
            "Content": "The new cafeteria is open."
        },
        "ToRecipients": [
            {
                "EmailAddress": {
                    "Address": "jdoe@contoso.onmicrosoft.com"
                }
            }
        ]
    },
    "SaveToSentItems": "false"
}

login_name = "mdoe@contoso.onmicrosoft.com"
client.users[login_name].send_mail(message_json)
client.execute_query()
```


# Working with OneDrive API

#### Documentation 

[OneDrive Graph API reference](https://docs.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0)

#### Authentication

[The Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/) which comes as a dependency 
is used to obtain token

```python
import msal

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
``` 


#### Examples 

##### Example: list available drives

The example demonstrates how to enumerate and print drive's url 
which corresponds to [`list available drives` endpoint](https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/drive_list?view=odsp-graph-online)

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)

```python
from office365.graph_client import GraphClient

tenant_name = "contoso.onmicrosoft.com"
client = GraphClient(acquire_token)
drives = client.drives
client.load(drives)
client.execute_query()
for drive in drives:
    print("Drive url: {0}".format(drive.web_url))
```


##### Example: download the contents of a DriveItem(folder facet)

```python
from office365.graph_client import GraphClient
client = GraphClient(acquire_token)
# retrieve drive properties 
drive = client.users["{user_id_or_principal_name}"].drive
client.load(drive)
client.execute_query()

# download files from OneDrive into local folder 
with tempfile.TemporaryDirectory() as path:
    download_files(drive.root, path)
```

where

```python
def download_files(remote_folder, local_path):
    drive_items = remote_folder.children
    client.load(drive_items)
    client.execute_query()
    for drive_item in drive_items:
        if not drive_item.file.is_server_object_null:  # is file?
            # download file content
            with open(os.path.join(local_path, drive_item.name), 'wb') as local_file:
                drive_item.download(local_file)
                client.execute_query()
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
tenant_name = "contoso.onmicrosoft.com"
client = GraphClient(tenant_name, acquire_token)
new_team = client.groups["{group_id}"].add_team()
client.execute_query()
```


# Third Party Libraries and Dependencies
The following libraries will be installed when you install the client library:
* [requests](https://github.com/kennethreitz/requests)
* [Microsoft Authentication Library (MSAL) for Python](https://pypi.org/project/msal/)




