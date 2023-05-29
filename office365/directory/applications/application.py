from office365.directory.applications.api import ApiApplication
from office365.directory.applications.public_client import PublicClientApplication
from office365.directory.applications.roles.role import AppRole
from office365.directory.applications.spa import SpaApplication
from office365.directory.certificates.certification import Certification
from office365.directory.object_collection import DirectoryObjectCollection
from office365.directory.object import DirectoryObject
from office365.directory.extensions.extension_property import ExtensionProperty
from office365.directory.key_credential import KeyCredential
from office365.directory.password_credential import PasswordCredential
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.types.collections import StringCollection


class Application(DirectoryObject):
    """
    Represents an application. Any application that outsources authentication to Azure Active Directory (Azure AD)
    must be registered in a directory. Application registration involves telling Azure AD about your application,
    including the URL where it's located, the URL to send replies after authentication,
    the URI to identify your application, and more. For more information, see Basics of Registering
    an Application in Azure AD
    """

    def add_password(self, display_name):
        """Adds a strong password to an application.

        :param str display_name: App display name
        """
        params = PasswordCredential(display_name=display_name)
        result = ClientResult(self.context, params)
        qry = ServiceOperationQuery(self, "addPassword", None, params, None, result)
        self.context.add_query(qry)
        return result

    def remove_password(self, key_id):
        """Remove a password from an application.

        :param str key_id: The unique identifier for the password.
        """
        qry = ServiceOperationQuery(self, "removePassword", None, {"keyId": key_id})
        self.context.add_query(qry)
        return self

    def delete_object(self, permanent_delete=False):
        """
        :param permanent_delete: Permanently deletes the application from directory
        :type permanent_delete: bool

        """
        super(Application, self).delete_object()
        if permanent_delete:
            deleted_item = self.context.directory.deleted_applications[self.id]
            deleted_item.delete_object()
        return self

    def set_verified_publisher(self, verified_publisher_id):
        """Set the verifiedPublisher on an application.
        For more information, including prerequisites to setting a verified publisher, see Publisher verification.

        :param str verified_publisher_id: The Microsoft Partner Network ID (MPNID) of the verified publisher
        to be set on the application, from the publisher's Partner Center account.
        """
        qry = ServiceOperationQuery(self, "setVerifiedPublisher", None, {"verifiedPublisherId": verified_publisher_id})
        self.context.add_query(qry)
        return self

    def unset_verified_publisher(self):
        """Unset the verifiedPublisher previously set on an application, removing all verified publisher properties.
        For more information, see Publisher verification.
        """
        qry = ServiceOperationQuery(self, "unsetVerifiedPublisher")
        self.context.add_query(qry)
        return self

    def add_key(self, key_credential, password_credential, proof):
        """
        Add a key credential to an application. This method, along with removeKey can be used by an application
        to automate rolling its expiring keys.

        :param KeyCredential key_credential: The new application key credential to add.
            The type, usage and key are required properties for this usage. Supported key types are:
                AsymmetricX509Cert: The usage must be Verify.
                X509CertAndPassword: The usage must be Sign
        :param PasswordCredential password_credential: Only secretText is required to be set which should contain
             the password for the key. This property is required only for keys of type X509CertAndPassword.
             Set it to null otherwise.
        :param str proof: A self-signed JWT token used as a proof of possession of the existing keys
        """
        payload = {
            "keyCredential": key_credential,
            "passwordCredential": password_credential,
            "proof": proof,
        }
        return_type = ClientResult(self.context, KeyCredential())
        qry = ServiceOperationQuery(self, "addKey", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_key(self, key_id, proof):
        """
        Remove a key credential from an application.
        This method along with addKey can be used by an application to automate rolling its expiring keys.

        :param str key_id: The unique identifier for the password.
        :param str proof: A self-signed JWT token used as a proof of possession of the existing keys.
             This JWT token must be signed using the private key of one of the application's existing
             valid certificates. The token should contain the following claims:
                 aud - Audience needs to be 00000002-0000-0000-c000-000000000000.
                 iss - Issuer needs to be the id of the application that is making the call.
                 nbf - Not before time.
                 exp - Expiration time should be "nbf" + 10 mins.
        """
        qry = ServiceOperationQuery(self, "removeKey", None, {"keyId": key_id, "proof": proof})
        self.context.add_query(qry)
        return self

    def update(self):
        self._ser_property_names.append("keyCredentials")
        return super(Application, self).update()

    @property
    def app_id(self):
        """The unique identifier for the application that is assigned to an application by Azure AD. Not nullable. """
        return self.properties.get("appId", None)

    @property
    def app_roles(self):
        """
        The collection of roles defined for the application. With app role assignments, these roles can be assigned to
        users, groups, or service principals associated with other applications
        """
        return self.properties.get("appRoles", ClientValueCollection(AppRole))

    @property
    def api(self):
        """Specifies settings for an application that implements a web API."""
        return self.properties.get("api", ApiApplication())

    @property
    def certification(self):
        """
        Specifies the certification status of the application.
        """
        return self.properties.get("certification", Certification())

    @property
    def spa(self):
        """
        Specifies settings for a single-page application, including sign out URLs and redirect URIs for
        authorization codes and access tokens."""
        return self.properties.get("spa", SpaApplication())

    @property
    def key_credentials(self):
        """The collection of key credentials associated with the application. Not nullable.
        """
        return self.properties.setdefault('keyCredentials', ClientValueCollection(KeyCredential))

    @property
    def display_name(self):
        """
        The display name for the application.
        Supports $filter (eq, ne, NOT, ge, le, in, startsWith), $search, and $orderBy.

        :rtype: str or None
        """
        return self.properties.get('displayName', None)

    @property
    def identifier_uris(self):
        """
        The URIs that identify the application within its Azure AD tenant, or within a verified custom domain
        if the application is multi-tenant. For more information see Application Objects and Service Principal Objects.
        The any operator is required for filter expressions on multi-valued properties.
        """
        return self.properties.get('identifierUris', StringCollection())

    @property
    def public_client(self):
        """
        Specifies settings for installed clients such as desktop or mobile devices.
        """
        return self.properties.get('publicClient', PublicClientApplication())

    @property
    def signin_audience(self):
        """
        Specifies the Microsoft accounts that are supported for the current application.
        Supported values are: AzureADMyOrg, AzureADMultipleOrgs, AzureADandPersonalMicrosoftAccount,
        PersonalMicrosoftAccount

        :rtype: str or None
        """
        return self.properties.get('signInAudience', None)

    @property
    def created_on_behalf_of(self):
        """"""
        return self.properties.get('createdOnBehalfOf',
                                   DirectoryObject(self.context, ResourcePath("createdOnBehalfOf", self.resource_path)))

    @property
    def owners(self):
        """Directory objects that are owners of the application.
        """
        return self.properties.get('owners',
                                   DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path)))

    @property
    def extension_properties(self):
        """List extension properties on an application object.
        """
        return self.properties.get('extensionProperties',
                                   EntityCollection(self.context, ExtensionProperty,
                                                    ResourcePath("extensionProperties", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "appRoles": self.app_roles,
                "createdOnBehalfOf": self.created_on_behalf_of,
                "extensionProperties": self.extension_properties,
                "keyCredentials": self.key_credentials,
                "publicClient": self.public_client
            }
            default_value = property_mapping.get(name, None)
        return super(Application, self).get_property(name, default_value)
