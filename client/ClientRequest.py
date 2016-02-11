import urlparse
import requests

class ClientRequest(object):
    """SharePoint client request"""


    def __init__(self,url,authContext):
        self.url = url
        self.defaultHeaders = {
            'content-type':'application/json;odata=verbose',
            'accept':'application/json;odata=verbose'
        }
        self.defaultHeaders['Cookie'] = authContext.getAuthenticationCookie()
        self.formDigestValue = None
        
    
    def executeQuery(self,requestUrl,headers={},data={}):
        "Execute client request" 
        try:
            url = self.url + requestUrl
            for key in self.defaultHeaders:
                headers[key] = self.defaultHeaders[key]
            if data or 'X-HTTP-Method' in headers:
                if not self.formDigestValue:
                    self.requestFormDigest()
                    headers['X-RequestDigest'] = self.formDigestValue
                result = requests.post(url=url,headers=headers,json = data)
            else:
                result = requests.get(url=url,headers=headers)
            if result.content:
                return result.json()
            return {}
        except requests.exceptions.RequestException as e:
            return "Error: {}".format(e)

    def requestFormDigest(self):
         "Request Form Digest"
         url = self.url + "/_api/contextinfo"
         result = requests.post(url=url,headers=self.defaultHeaders)
         json = result.json()
         self.formDigestValue = json['d']['GetContextWebInformation']['FormDigestValue']
         

        

  




