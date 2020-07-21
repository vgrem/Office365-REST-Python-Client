import os
import uuid
from xml.etree import ElementTree

import requests
import requests.utils

import office365.logger
from office365.runtime.auth.base_token_provider import BaseTokenProvider
from office365.runtime.auth.sts_profile import STSProfile
from office365.runtime.auth.user_realm_info import UserRealmInfo

office365.logger.ensure_debug_secrets()


def resolve_base_url(url):
    parts = url.split('://')
    host_name = parts[1].split("/")[0]
    return parts[0] + '://' + host_name


class SamlTokenProvider(BaseTokenProvider, office365.logger.LoggerContext):

    def __init__(self, url, username, password):
        """SAML Security Token Service provider

        :type password: str
        :type username: str
        :type url: str
        """
        self.__username = username
        self.__password = password
        # Security Token Service info
        self.__sts_profile = STSProfile(resolve_base_url(url))
        # Last occurred error
        self.error = ''
        self._auth_cookies = {}
        self.__ns_prefixes = {
            'S': '{http://www.w3.org/2003/05/soap-envelope}',
            's': '{http://www.w3.org/2003/05/soap-envelope}',
            'psf': '{http://schemas.microsoft.com/Passport/SoapServices/SOAPFault}',
            'wst': '{http://schemas.xmlsoap.org/ws/2005/02/trust}',
            'wsse': '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd}',
            'saml': '{urn:oasis:names:tc:SAML:1.0:assertion}',
            'u': '{http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd}',
            'wsa': '{http://www.w3.org/2005/08/addressing}',
            'wsp': '{http://schemas.xmlsoap.org/ws/2004/09/policy}',
            'ps': '{http://schemas.microsoft.com/LiveID/SoapServices/v1}',
            'ds': '{http://www.w3.org/2000/09/xmldsig#}'
        }
        for key in self.__ns_prefixes.keys():
            ElementTree.register_namespace(key, self.__ns_prefixes[key][1:-1])

    def is_authenticated(self):
        return any(self._auth_cookies)

    def acquire_token(self, **kwargs):
        """Acquire user token
        """
        logger = self.logger(self.acquire_token.__name__)
        logger.debug('acquire_token called')

        try:
            logger.debug("Acquiring Access Token..")
            user_realm = self._get_user_realm(self.__username)
            if user_realm.IsFederated:
                token = self.acquire_service_token_from_adfs(user_realm.STSAuthUrl, self.__username, self.__password)
            else:
                token = self._acquire_service_token(self.__username, self.__password)
            return self._acquire_authentication_cookie(token, user_realm.IsFederated)
        except requests.exceptions.RequestException as e:
            self.error = "Error: {}".format(e)
            return False

    def _get_user_realm(self, login):
        """Get User Realm

        :type login: str
        """
        response = requests.post(self.__sts_profile.user_realm_service_url, data="login={0}&xml=1".format(login),
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
        xml = ElementTree.fromstring(response.content)
        node = xml.find('NameSpaceType')
        if node is not None:
            if node.text == 'Federated':
                info = UserRealmInfo(xml.find('STSAuthURL').text, True)
            else:
                info = UserRealmInfo(None, False)
            return info
        return None

    def get_authentication_cookie(self):
        """Build auth cookie"""
        logger = self.logger(self.get_authentication_cookie.__name__)
        logger.debug_secrets(self._auth_cookies)
        return "; ".join(["=".join([key, str(val)]) for key, val in self._auth_cookies.items()])

    def get_last_error(self):
        return self.error

    def acquire_service_token_from_adfs(self, adfs_url, username, password):
        logger = self.logger(self.acquire_service_token_from_adfs.__name__)
        payload = self._prepare_request_from_template('FederatedSAML.xml', {
            'auth_url': adfs_url,
            'username': username,
            'password': password,
            'message_id': str(uuid.uuid4()),
            'created': self.__sts_profile.created,
            'expires': self.__sts_profile.expires,
            'issuer': self.__sts_profile.federationTokenIssuer
        })
        response = requests.post(adfs_url, data=payload,
                                 headers={'Content-Type': 'application/soap+xml; charset=utf-8'})
        try:
            xml = ElementTree.fromstring(response.content)
            # 1.find assertion
            assertion_node = xml.find(
                '{0}Body/{1}RequestSecurityTokenResponse/{1}RequestedSecurityToken/{2}Assertion'.format(
                    self.__ns_prefixes['s'], self.__ns_prefixes['wst'], self.__ns_prefixes['saml']))
            if assertion_node is None:
                self.error = 'Cannot get security assertion for user {0} from {1}'.format(self.__username, adfs_url)
                logger.error(self.error)
                return None
            # 2. prepare & submit token request
            self.__sts_profile.signInPage = '_vti_bin/idcrl.svc/'
            self.__sts_profile.securityTokenServicePath = 'rst2.srf'
            template = self._prepare_request_from_template('RST2.xml', {
                'auth_url': self.__sts_profile.authorityUrl,
                'serviceTokenUrl': self.__sts_profile.security_token_service_url
            })
            template_xml = ElementTree.fromstring(template)
            security_node = template_xml.find(
                '{0}Header/{1}Security'.format(self.__ns_prefixes['s'], self.__ns_prefixes['wsse']))

            security_node.insert(1, assertion_node)
            payload = ElementTree.tostring(template_xml).decode()
            # 3. get token
            response = requests.post(self.__sts_profile.security_token_service_url, data=payload,
                                     headers={'Content-Type': 'application/soap+xml'})
            token = self._process_service_token_response(response)
            logger.debug_secrets('security token: %s', token)
            return token
        except ElementTree.ParseError as e:
            self.error = 'An error occurred while parsing the server response: {}'.format(e)
            logger.error(self.error)
            return None

    def _acquire_service_token(self, username, password, service_target=None, service_policy=None):
        """Retrieve service token"""
        logger = self.logger(self._acquire_service_token.__name__)
        payload = self._prepare_request_from_template('SAML.xml', {
            'auth_url': self.__sts_profile.authorityUrl,
            'username': username,
            'password': password,
            'message_id': str(uuid.uuid4()),
            'created': self.__sts_profile.created,
            'expires': self.__sts_profile.expires,
            'issuer': self.__sts_profile.federationTokenIssuer
        })
        logger.debug_secrets('options: %s', payload)
        response = requests.post(self.__sts_profile.security_token_service_url, data=payload,
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'})
        token = self._process_service_token_response(response)
        logger.debug_secrets('security token: %s', token)
        return token

    def _process_service_token_response(self, response):
        logger = self.logger(self._process_service_token_response.__name__)
        logger.debug_secrets('response: %s\nresponse.content: %s', response, response.content)

        try:
            xml = ElementTree.fromstring(response.content)
        except ElementTree.ParseError as e:
            self.error = 'An error occurred while parsing the server response: {}'.format(e)
            logger.error(self.error)
            return None

        # check for errors
        if xml.find('{0}Body/{0}Fault'.format(self.__ns_prefixes['s'])) is not None:
            error = xml.find(
                '{0}Body/{0}Fault/{0}Detail/{1}error/{1}internalerror/{1}text'.format(self.__ns_prefixes['s'],
                                                                                      self.__ns_prefixes['psf']))
            if error is None:
                self.error = 'An error occurred while retrieving token from XML response.'
            else:
                self.error = 'An error occurred while retrieving token from XML response: {0}'.format(error.text)
            logger.error(self.error)
            return None

        # extract token
        token = xml.find(
            '{0}Body/{1}RequestSecurityTokenResponse/{1}RequestedSecurityToken/{2}BinarySecurityToken'.format(
                self.__ns_prefixes['s'], self.__ns_prefixes['wst'], self.__ns_prefixes['wsse']))
        if token is None:
            self.error = 'Cannot get binary security token for from {0}'.format(
                self.__sts_profile.security_token_service_url)
            logger.error(self.error)
            return None
        logger.debug_secrets("token: %s", token)
        return token.text

    def _acquire_authentication_cookie(self, security_token, federated=False):
        """Retrieve auth cookie from STS

        :type federated: bool
        :type security_token: str
        """
        logger = self.logger(self._acquire_authentication_cookie.__name__)
        session = requests.session()
        logger.debug_secrets("session: %s\nsession.post(%s, data=%s)", session, self.__sts_profile.signin_page_url,
                             security_token)
        if not federated:
            self._auth_cookies['FedAuth'] = None
            self._auth_cookies['rtFa'] = None
            session.post(self.__sts_profile.signin_page_url, data=security_token,
                         headers={'Content-Type': 'application/x-www-form-urlencoded'})
        else:
            self._auth_cookies['SPOIDCRL'] = None
            session.get(self.__sts_profile.signin_page_url,
                        headers={
                            'User-Agent': 'Office365 Python Client',
                            'X-IDCRL_ACCEPTED': 't',
                            'Authorization': 'BPOSIDCRL {0}'.format(security_token)
                        })
        logger.debug_secrets("session.cookies: %s", session.cookies)
        cookies = requests.utils.dict_from_cookiejar(session.cookies)
        logger.debug_secrets("cookies: %s", cookies)
        if not cookies:
            self.error = "An error occurred while retrieving auth cookies from {0}".format(
                self.__sts_profile.signin_page_url)
            logger.error(self.error)
            return False
        for name in self._auth_cookies.keys():
            self._auth_cookies[name] = cookies[name]
        return True

    @staticmethod
    def _prepare_request_from_template(template_name, params):
        """Construct the request body to acquire security token from STS endpoint"""
        logger = SamlTokenProvider.logger()
        logger.debug_secrets('params: %s', params)
        f = open(os.path.join(os.path.dirname(__file__), "templates", template_name))
        try:
            data = f.read()
            for key in params:
                data = data.replace('{' + key + '}', str(params[key]))
            return data
        finally:
            f.close()
