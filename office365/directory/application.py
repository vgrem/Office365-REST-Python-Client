from office365.directory.directoryObject import DirectoryObject
from office365.directory.keyCredential import KeyCredential
from office365.runtime.client_value_collection import ClientValueCollection


class Application(DirectoryObject):
    """
    Represents an application. Any application that outsources authentication to Azure Active Directory (Azure AD)
    must be registered in a directory. Application registration involves telling Azure AD about your application,
    including the URL where it's located, the URL to send replies after authentication,
    the URI to identify your application, and more. For more information, see Basics of Registering
    an Application in Azure AD
    """

    @property
    def key_credentials(self):
        """The collection of key credentials associated with the application. Not nullable.
        """
        return self.properties.get('keyCredentials', ClientValueCollection(KeyCredential))
