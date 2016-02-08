import os
from xml.etree import ElementTree
import requests, requests.utils, urlparse

class AuthenticationContext(object):
    """SharePoint Online Authentication Context"""

    def __init__(self,url):

        self.url = url

        #External Security Token Service for SPO
        self.sts = {
           'host': 'login.microsoftonline.com',
           'path': '/extSTS.srf'
        }
    
        #Sign in page url
        self.login = '/_forms/default.aspx?wa=wsignin1.0'

        #Last occured error
        self.error = ''


    def acquireTokenForUser(self,username, password):
        "Acquire user token"
        try:
            url = urlparse.urlparse(self.url)  
            options = {
                'username': username,
                'password': password,
                'sts': self.sts,
                'endpoint': url.scheme + '://' + url.hostname + self.login
            }
            
            if self.acquireServiceToken(options) and self.acquireAuthenticationCookie(options):
                self.FedAuth = options['FedAuth']
                self.rtFa = options['rtFa']
                return True
            return False
        except requests.exceptions.RequestException as e:
           self.error = "Error: {}".format(e)
           return False
           
      
    def getAuthenticationCookie(self):
        "Generate Auth Cookie"
        return 'FedAuth=' + self.FedAuth + '; rtFa=' + self.rtFa

    def getLastErrorMessage(self):
        return self.error

    def acquireServiceToken(self,options):
        "Retrieve serice token"
        samlMessage = self.prepareSamlMessage({
             'username': options['username'],
             'password': options['password'],
             'endpoint': self.url
            })
    
        stsUrl = 'https://' + options['sts']['host'] + options['sts']['path']    
        response = requests.post(stsUrl, data = samlMessage)
        token = self.processServiceTokenResponse(response)
        if(token):
            self.token = token
            return True
        return False
             
    def processServiceTokenResponse(self,response):
        xml = ElementTree.fromstring(response.content)
        nsPrefixes = { 'S': '{http://www.w3.org/2003/05/soap-envelope}',
                          'psf' : '{http://schemas.microsoft.com/Passport/SoapServices/SOAPFault}',
                          'wst': '{http://schemas.xmlsoap.org/ws/2005/02/trust}',
                          'wsse': '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}' }

        #check for errors 
        if xml.find('{0}Body/{0}Fault'.format(nsPrefixes['S'])) is not None :
            error = xml.find('{0}Body/{0}Fault/{0}Detail/{1}error/{1}internalerror/{1}text'.format(nsPrefixes['S'],nsPrefixes['psf']))
            self.error ='An error occured while retrieving token: {0}'.format(error.text)
            return None

        #extract token
        token = xml.find('{0}Body/{1}RequestSecurityTokenResponse/{1}RequestedSecurityToken/{2}BinarySecurityToken'.format(nsPrefixes['S'],nsPrefixes['wst'],nsPrefixes['wsse']))
        return token.text

    def acquireAuthenticationCookie(self,options):
        "Retrieve SPO auth cookie"
        url = options['endpoint']
     
        session = requests.session()
        response = session.post(url, data = self.token)
        cookies = requests.utils.dict_from_cookiejar(session.cookies);
        if 'FedAuth' in cookies and 'rtFa' in cookies:
            options['FedAuth'] = cookies['FedAuth']
            options['rtFa'] = cookies['rtFa']
            return True
        self.error = "An error occured while retrieving auth cookies" 
        return False

    def prepareSamlMessage(self,params):
        "Read & prepare SAML WS template" 
        f = open(os.path.join(os.path.dirname(__file__), 'SAML.xml'))
        saml = f.read()
        for key in params:
            saml = saml.replace('[' + key + ']', params[key]);
        return saml