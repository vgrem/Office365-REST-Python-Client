import os
import urlparse
from xml.etree import ElementTree
import requests
import requests.utils
from client.office365.runtime.auth.base_token_provider import BaseTokenProvider


class SamlTokenProvider(BaseTokenProvider):
    """ SAML Security Token Service for O365"""

    def __init__(self, url, username, password):

        self.url = url
        self.username = username
        self.password = password

        # External Security Token Service for SPO
        self.sts = {
            'host': 'login.microsoftonline.com',
            'path': '/extSTS.srf'
        }

        # Sign in page url
        self.login = '/_forms/default.aspx?wa=wsignin1.0'

        # Last occurred error
        self.error = ''

        self.token = None
        self.FedAuth = None
        self.rtFa = None

    def acquire_token(self):
        """Acquire user token"""
        try:
            url = urlparse.urlparse(self.url)
            options = {
                'username': self.username,
                'password': self.password,
                'sts': self.sts,
                'endpoint': url.scheme + '://' + url.hostname + self.login
            }

            self.acquire_service_token(options)
            self.acquire_authentication_cookie(options)
            return True
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def get_authentication_cookie(self):
        """Generate Auth Cookie"""
        return 'FedAuth=' + self.FedAuth + '; rtFa=' + self.rtFa

    def get_last_error(self):
        return self.error

    def acquire_service_token(self, options):
        """Retrieve service token"""
        request_body = self.prepare_security_token_request({
            'username': options['username'],
            'password': options['password'],
            'endpoint': self.url
        })

        sts_url = 'https://' + options['sts']['host'] + options['sts']['path']
        response = requests.post(sts_url, data=request_body)
        token = self.process_service_token_response(response)
        if token:
            self.token = token
            return True
        return False

    def process_service_token_response(self, response):
        xml = ElementTree.fromstring(response.content)
        ns_prefixes = {'S': '{http://www.w3.org/2003/05/soap-envelope}',
                       'psf': '{http://schemas.microsoft.com/Passport/SoapServices/SOAPFault}',
                       'wst': '{http://schemas.xmlsoap.org/ws/2005/02/trust}',
                       'wsse': '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}'}

        # check for errors
        if xml.find('{0}Body/{0}Fault'.format(ns_prefixes['S'])) is not None:
            error = xml.find('{0}Body/{0}Fault/{0}Detail/{1}error/{1}internalerror/{1}text'.format(ns_prefixes['S'],
                                                                                                   ns_prefixes['psf']))
            self.error = 'An error occurred while retrieving token: {0}'.format(error.text)
            return None

        # extract token
        token = xml.find(
            '{0}Body/{1}RequestSecurityTokenResponse/{1}RequestedSecurityToken/{2}BinarySecurityToken'.format(
                ns_prefixes['S'], ns_prefixes['wst'], ns_prefixes['wsse']))
        return token.text

    def acquire_authentication_cookie(self, options):
        """Retrieve SPO auth cookie"""
        url = options['endpoint']

        session = requests.session()
        session.post(url, data=self.token)
        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        if 'FedAuth' in cookies and 'rtFa' in cookies:
            self.FedAuth = cookies['FedAuth']
            self.rtFa = cookies['rtFa']
            return True
        self.error = "An error occurred while retrieving auth cookies"
        return False

    @staticmethod
    def prepare_security_token_request(params):
        """Construct the request body to acquire security token from STS endpoint"""
        f = open(os.path.join(os.path.dirname(__file__), 'SAML.xml'))
        data = f.read()
        for key in params:
            data = data.replace('[' + key + ']', params[key])
        return data
