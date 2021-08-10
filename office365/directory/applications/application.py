from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.directory.directory_object import DirectoryObject
from office365.directory.extensions.extension_property import ExtensionProperty
from office365.directory.key_credential import KeyCredential
from office365.directory.password_credential import PasswordCredential
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


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
        """Remove a password from an application."""
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
