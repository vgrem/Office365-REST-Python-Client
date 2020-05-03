# About
Office 365 & Microsoft Graph Library for Python

# Usage

1.   [Installation](#Installation)
1.   [Working with SharePoint API](#Working-with-SharePoint-API) 
2.   [Working with Outlook API](#Working-with-Outlook-API) 
3.   [Working with OneDrive API](#Working-with-OneDrive-API)    


## Status

[![Downloads](https://pepy.tech/badge/office365-rest-python-client)](https://pepy.tech/project/office365-rest-python-client)
[![PyPI](https://img.shields.io/pypi/v/Office365-REST-Python-Client.svg)](https://pypi.python.org/pypi/Office365-REST-Python-Client)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/Office365-REST-Python-Client.svg)](https://pypi.python.org/pypi/Office365-REST-Python-Client/)
[![Build Status](https://travis-ci.org/vgrem/Office365-REST-Python-Client.svg?branch=master)](https://travis-ci.org/vgrem/Office365-REST-Python-Client)

# Installation

Use pip:

```
pip install Office365-REST-Python-Client
```


# Working with SharePoint API

The list of supported API versions: 
-   [SharePoint 2013 REST API](https://msdn.microsoft.com/en-us/library/office/jj860569.aspx) and above 
-   SharePoint Online & OneDrive for Business REST API

#### Authentication

The following auth flows are supported:

- app principals auth (refer [Granting access using SharePoint App-Only](https://docs.microsoft.com/en-us/sharepoint/dev/solution-guidance/security-apponly-azureacs) for a details): `AuthenticationContext.ctx_auth.acquire_token_for_app(client_id, client_secret)`
- user credentials auth: `AuthenticationContext.ctx_auth.acquire_token_for_user(username, password)`


#### Examples
 

There are **two approaches** available to perform API queries:

1. `ClientContext class` - where you target SharePoint resources such as `Web`, `ListItem` and etc (recommended)
 

   ```

    from office365.sharepoint.client_context import ClientContext

    ctx = ClientContext.connect_with_credentials(url,UserCredential(username, password))
    web = ctx.web
    ctx.load(web)
    ctx.execute_query()
    print "Web title: {0}".format(web.properties['Title'])
   ```

2. `RequestOptions class` - where you construct REST queries (and no model is involved)

   The example demonstrates how to read `Web` properties:
   
   

```
import json
from office365.runtime.auth.UserCredential import UserCredential
from office365.runtime.http.request_options import RequestOptions
from office365.sharepoint.client_context import ClientContext

ctx = ClientContext.connect_with_credentials(url,UserCredential(username, password))
request = RequestOptions("{0}/_api/web/".format(settings['url']))
response = ctx.execute_request_direct(request)
json = json.loads(response.content)
web_title = json['d']['Title']
print("Web title: {0}".format(web_title))

```


# Working with Outlook API

The list of supported APIs:
-   [Outlook Contacts REST API](https://msdn.microsoft.com/en-us/office/office365/api/contacts-rest-operations)
-   [Outlook Calendar REST API](https://msdn.microsoft.com/en-us/office/office365/api/calendar-rest-operations)
-   [Outlook Mail REST API](https://msdn.microsoft.com/en-us/office/office365/api/mail-rest-operations)


Since Outlook REST APIs are available in both Microsoft Graph and the Outlook API endpoint, 
the following clients are available:

- `GraphClient` which targets Outlook `v2.0` version (*preferable* nowadays, refer [transition to Microsoft Graph-based Outlook REST API](https://docs.microsoft.com/en-us/outlook/rest/compare-graph-outlook) for a details)   
- `OutlookClient` which targets Outlook `v1.0` version (not recommended for usage since `v1.0` version is being deprecated.)


#### Authentication

[ADAL Python](https://adal-python.readthedocs.io/en/latest/#) 
library is utilized to authenticate users to Active Directory (AD) and obtain tokens


#### Example

The example demonstrates how to send an email via [Microsoft Graph endpoint](https://docs.microsoft.com/en-us/graph/api/user-sendmail?view=graph-rest-1.0&tabs=http).

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)

```
def get_token(auth_ctx):
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        client_id,
        client_secret)
    return token


tenant_name = "contoso.onmicrosoft.com"
client = GraphClient(tenant_name, get_token)

message_payload = {
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
client.users[login_name].send_mail(message_payload)
client.execute_query()
```


# Working with OneDrive API

#### Documentation 

[OneDrive Graph API reference](https://docs.microsoft.com/en-us/graph/api/resources/onedrive?view=graph-rest-1.0)

#### Authentication

[ADAL Python](https://adal-python.readthedocs.io/en/latest/#) 
library is utilized to authenticate users to Active Directory (AD) and obtain tokens  

#### Example 
The example demonstrates how to print drive's url via [`list available drives` endpoint](https://docs.microsoft.com/en-us/onedrive/developer/rest-api/api/drive_list?view=odsp-graph-online)

> Note: access token is getting acquired  via [Client Credential flow](https://docs.microsoft.com/en-us/azure/active-directory/develop/v2-oauth2-client-creds-grant-flow)

```
def get_token(auth_ctx):
    """Acquire token via client credential flow (ADAL Python library is utilized)"""
    token = auth_ctx.acquire_token_with_client_credentials(
        "https://graph.microsoft.com",
        client_id,
        client_secret)
    return token


tenant_name = "contoso.onmicrosoft.com"
client = GraphClient(tenant_name, get_token)
drives = client.drives
client.load(drives)
client.execute_query()
for drive in drives:
    print("Drive url: {0}".format(drive.web_url))
```


# Third Party Libraries and Dependencies
The following libraries will be installed when you install the client library:
* [requests](https://github.com/kennethreitz/requests)
* [adal](https://github.com/AzureAD/azure-activedirectory-library-for-python)




