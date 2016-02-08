# About
This is a SharePoint Online REST API client for Python


# Installation

Todo


# Usage

The first example demonstrates how to read Web client object

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

# Python Version
Python 2.7 is fully supported.


# Third Party Libraries and Dependencies
The following libraries will be installed when you install the client library:
* [requests](https://github.com/kennethreitz/requests)




