from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.directory.directory_object import DirectoryObject
from office365.runtime.paths.resource_path import ResourcePath


class ServicePrincipal(DirectoryObject):
    """Represents an instance of an application in a directory."""

    def add_key(self, key_credential, password_credential, proof):
        pass

    def add_password(self):
        pass

    @property
    def app_display_name(self):
        """The collection of key credentials associated with the application. Not nullable.
        """
        return self.properties.get('appDisplayName', None)

    @property
    def service_principal_type(self):
        """
        Identifies whether the service principal represents an application, a managed identity, or a legacy application.
        This is set by Azure AD internally. The servicePrincipalType property can be set to three different values:
            Application - A service principal that represents an application or service.
            The appId property identifies the associated app registration, and matches the appId of an application,
            possibly from a different tenant. If the associated app registration is missing, tokens are not issued
            for the service principal.

            ManagedIdentity - A service principal that represents a managed identity. Service principals
            representing managed identities can be granted access and permissions, but cannot be updated
            or modified directly.

            Legacy - A service principal that represents an app created before app registrations,
            or through legacy experiences. Legacy service principal can have credentials, service principal names,
            reply URLs, and other properties which are editable by an authorized user,
            but does not have an associated app registration. The appId value does not associate
            the service principal with an app registration.
            The service principal can only be used in the tenant where it was created.

        :rtype: str or None
        """
        return self.properties.get('servicePrincipalType', None)

    @property
    def owners(self):
        """Directory objects that are owners of this servicePrincipal.
        The owners are a set of non-admin users or servicePrincipals who are allowed to modify this object.

        :rtype: DirectoryObjectCollection
        """
        return self.get_property('owners',
                                 DirectoryObjectCollection(self.context, ResourcePath("owners", self.resource_path)))
