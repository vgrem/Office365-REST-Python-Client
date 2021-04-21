from office365.directory.directoryObject import DirectoryObject
from office365.directory.keyCredential import KeyCredential
from office365.directory.passwordCredential import PasswordCredential
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery


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
        return_type = PasswordCredential(displayName=display_name)
        qry = ServiceOperationQuery(self, "addPassword", None, return_type, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove_password(self, keyId):
        """Remove a password from an application."""
        qry = ServiceOperationQuery(self, "removePassword", None, {"keyId": keyId})
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
