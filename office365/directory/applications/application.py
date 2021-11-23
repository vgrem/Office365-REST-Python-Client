from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.directory.directory_object import DirectoryObject
from office365.directory.extensions.extension_property import ExtensionProperty
from office365.directory.key_credential import KeyCredential
from office365.directory.password_credential import PasswordCredential
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath


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
        params = PasswordCredential(displayName=display_name)
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
        :param PasswordCredential password_credential: Only secretText is required to be set which should contain the password
             for the key. This property is required only for keys of type X509CertAndPassword. Set it to null otherwise.
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

    @property
    def key_credentials(self):
        """The collection of key credentials associated with the application. Not nullable.
        """
        return self.properties.get('keyCredentials', ClientValueCollection(KeyCredential))

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
        return self.properties.get('identifierUris', ClientValueCollection(str))

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
    def owners(self):
        """Directory objects that are owners of the application. Read-only.

        :rtype: DirectoryObjectCollection
        """
        return self.get_property('owners',
                                 DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path)))

    @property
    def extension_properties(self):
        """List extension properties on an application object.

        :rtype: EntityCollection
        """
        return self.get_property('extensionProperties',
                                 EntityCollection(self.context, ExtensionProperty,
                                                  ResourcePath("extensionProperties", self.resource_path)))
