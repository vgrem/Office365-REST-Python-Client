import os
from xml.etree import ElementTree

import requests
import requests.utils

import office365.logger
from office365.runtime.auth.base_token_provider import BaseTokenProvider

office365.logger.ensure_debug_secrets()


class SamlTokenProvider(BaseTokenProvider, office365.logger.LoggerContext):
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
        logger = self.logger(self.acquire_token.__name__)
        logger.debug('called')

        try:
            logger.debug("Acquiring Access Token..")
            try:
                from urlparse import urlparse  # Python 2.X
            except ImportError:
                from urllib.parse import urlparse  # Python 3+
            url = urlparse(self.url)
            options = {
                'username': self.username,
                'password': self.password,
                'sts': self.sts,
                'endpoint': url.scheme + '://' + url.hostname + self.login
            }

            if not self.acquire_service_token(options):
                return False
            if not self.acquire_authentication_cookie(options):
                return False
            return True
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def get_authentication_cookie(self):
        """Generate Auth Cookie"""
        logger = self.logger(self.get_authentication_cookie.__name__)

        logger.debug_secrets("self.FedAuth: %s\nself.rtFa: %s", self.FedAuth, self.rtFa)
        return 'FedAuth=' + self.FedAuth + '; rtFa=' + self.rtFa

    def get_last_error(self):
        return self.error

    def acquire_service_token(self, options):
        """Retrieve service token"""
        logger = self.logger(self.acquire_service_token.__name__)
        logger.debug_secrets('options: %s', options)

        request_body = self.prepare_security_token_request({
            'username': options['username'],
            'password': options['password'],
            'endpoint': self.url
        })

        sts_url = 'https://' + options['sts']['host'] + options['sts']['path']
        response = requests.post(sts_url, data=request_body,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
        token = self.process_service_token_response(response)
        logger.debug_secrets('token: %s', token)
        if token:
            self.token = token
            return True
        return False

    def process_service_token_response(self, response):
        logger = self.logger(self.process_service_token_response.__name__)
        logger.debug_secrets('response: %s\nresponse.content: %s', response, response.content)

        try:
            xml = ElementTree.fromstring(response.content)
        except ElementTree.ParseError as e:
            self.error = 'An error occurred while parsing the server response: {}'.format(e)
            logger.error(self.error)
            return None

        ns_prefixes = {'S': '{http://www.w3.org/2003/05/soap-envelope}',
                       'psf': '{http://schemas.microsoft.com/Passport/SoapServices/SOAPFault}',
                       'wst': '{http://schemas.xmlsoap.org/ws/2005/02/trust}',
                       'wsse': '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}'}
        logger.debug_secrets("ns_prefixes: %s", ns_prefixes)

        # check for errors
        if xml.find('{0}Body/{0}Fault'.format(ns_prefixes['S'])) is not None:
            error = xml.find('{0}Body/{0}Fault/{0}Detail/{1}error/{1}internalerror/{1}text'.format(ns_prefixes['S'],
                                                                                                   ns_prefixes['psf']))
            self.error = 'An error occurred while retrieving token: {0}'.format(error.text)
            logger.error(self.error)
            return None

        # extract token
        token = xml.find(
            '{0}Body/{1}RequestSecurityTokenResponse/{1}RequestedSecurityToken/{2}BinarySecurityToken'.format(
                ns_prefixes['S'], ns_prefixes['wst'], ns_prefixes['wsse']))
        logger.debug_secrets("token: %s", token)
        return token.text

    def acquire_authentication_cookie(self, options):
        """Retrieve SPO auth cookie"""
        logger = self.logger(self.acquire_authentication_cookie.__name__)

        url = options['endpoint']

        session = requests.session()
        logger.debug_secrets("session: %s\nsession.post(%s, data=%s)", session, url, self.token)
        session.post(url, data=self.token, headers={'Content-Type': 'application/x-www-form-urlencoded'})
        logger.debug_secrets("session.cookies: %s", session.cookies)
        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        logger.debug_secrets("cookies: %s", cookies)
        if 'FedAuth' in cookies and 'rtFa' in cookies:
            self.FedAuth = cookies['FedAuth']
            self.rtFa = cookies['rtFa']
            return True
        self.error = "An error occurred while retrieving auth cookies"
        logger.error(self.error)
        return False

    @staticmethod
    def prepare_security_token_request(params):
        """Construct the request body to acquire security token from STS endpoint"""
        logger = SamlTokenProvider.logger(SamlTokenProvider.prepare_security_token_request.__name__)
        logger.debug_secrets('params: %s', params)

        f = open(os.path.join(os.path.dirname(__file__), 'SAML.xml'))
        try:
            data = f.read()
            for key in params:
                data = data.replace('[' + key + ']', params[key])
            return data
        finally:
            f.close()
