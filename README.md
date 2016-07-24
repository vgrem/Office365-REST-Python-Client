# About
SharePoint Online REST API client for Python

## Status

[![Build Status](https://travis-ci.org/vgrem/SharePointOnline-REST-Python-Client.svg?branch=master)](https://travis-ci.org/vgrem/SharePointOnline-REST-Python-Client)

# Installation

Todo


# Usage 

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




