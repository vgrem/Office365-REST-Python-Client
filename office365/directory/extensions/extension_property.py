from office365.directory.directory_object import DirectoryObject


class ExtensionProperty(DirectoryObject):
    """
    Represents a directory extension that can be used to add a custom property to directory objects without
    requiring an external data store. For example, if an organization has a line of business (LOB) application
    that requires a Skype ID for each user in the directory, Microsoft Graph can be used to register a new property
    named skypeId on the directory’s User object, and then write a value to the new property for a specific user.
    """
    pass
