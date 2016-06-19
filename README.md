# About
SharePoint Online REST API client for Python

## Status

[![Build Status](https://travis-ci.org/vgrem/SharePointOnline-REST-Python-Client.svg?branch=master)](https://github.com/vgrem/SharePointOnline-REST-Python-Client)

# Installation

Todo


# Usage 

There are **two approaches** available to perform REST queries:

1) via `ClientRequest class` where you need to construct REST queries by specifying endpoint url, headers if required and payload (aka low level approach)

The first example demonstrates how to read Web resource:

```
ctxAuth = AuthenticationContext(url)
if ctxAuth.acquireTokenForUser(username, password):
  request = ClientRequest(url,ctxAuth)
  requestUrl = "/_api/web/"   #Web resource endpoint
  data = request.executeQuery(requestUrl=requestUrl)

  webTitle = data['d']['Title']
  print "Web title: {0}".format(webTitle)

else:
  print ctxAuth.getLastErrorMessage()
```

2) via `ClientContext class` where you target client object resources such as Web, ListItem and etc.
 

```
ctxAuth = AuthenticationContext(url)
if ctxAuth.acquireTokenForUser(username, password):
  ctx = ClientContext(url, ctxAuth)   
  web = ctx.web
  ctx.load(web)
  ctx.execute_query()
  print "Web title: {0}".format(web.properties['Title'])

else:
  print ctxAuth.getLastErrorMessage()
```


# Python Version
Python 2.7 is fully supported.


# Third Party Libraries and Dependencies
The following libraries will be installed when you install the client library:
* [requests](https://github.com/kennethreitz/requests)




