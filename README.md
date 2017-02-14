# About
Office365 REST API client for Python

The list of supported Office 365 REST APIs:

-   [SharePoint REST API](https://msdn.microsoft.com/en-us/library/office/jj860569.aspx) (_supported_ versions: [SharePoint 2013](https://msdn.microsoft.com/library/office/jj860569(v=office.15).aspx), SharePoint 2016, SharePoint Online and OneDrive for Business)
-   [Outlook REST API](https://msdn.microsoft.com/en-us/office/office365/api/use-outlook-rest-api#DefineOutlookRESTAPI) 
    -   [Outlook Contacts REST API](https://msdn.microsoft.com/en-us/office/office365/api/contacts-rest-operations)
    -   [Outlook Calendar REST API](https://msdn.microsoft.com/en-us/office/office365/api/calendar-rest-operations)
    -   [Outlook Mail REST API](https://msdn.microsoft.com/en-us/office/office365/api/mail-rest-operations)


## Status

[![Build Status](https://travis-ci.org/vgrem/Office365-REST-Python-Client.svg?branch=master)](https://travis-ci.org/vgrem/Office365-REST-Python-Client)

# Installation

Use pip:

```
pip install Office365-REST-Python-Client
```


# Usage: working with SharePoint resources 

There are **two approaches** available to perform REST queries:

1) via `ClientRequest class` where you need to construct REST queries by specifying endpoint url, headers if required and payload (aka low level approach)

The first example demonstrates how to read Web resource:

```
ctx_auth = AuthenticationContext(url)
if ctx_auth.acquireTokenForUser(username, password):
  request = ClientRequest(url,ctx_auth)
  requestUrl = "/_api/web/"   #Web resource endpoint
  data = request.execute_query_direct(requestUrl=requestUrl)
  web_title = data['d']['Title']
  print "Web title: {0}".format(web_title)

else:
  print ctx_auth.get_last_error()
```

2) via `ClientContext class` where you target client object resources such as Web, ListItem and etc.
 

```
ctx_auth = AuthenticationContext(url)
if ctx_auth.acquireTokenForUser(username, password):
  ctx = ClientContext(url, ctx_auth)   
  web = ctx.web
  ctx.load(web)
  ctx.execute_query()
  print "Web title: {0}".format(web.properties['Title'])

else:
  print ctx_auth.get_last_error()
```


# Python Version
Python 2.7 is fully supported.


# Third Party Libraries and Dependencies
The following libraries will be installed when you install the client library:
* [requests](https://github.com/kennethreitz/requests)




