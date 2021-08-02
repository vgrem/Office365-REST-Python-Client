from office365.directory.extension import ExtensionCollection
from office365.mail.item import Item
from office365.runtime.resource_path import ResourcePath


class Contact(Item):
    """User's contact."""

    @property
    def manager(self):
        """
        The name of the contact's manager.
        :rtype: str or None
        """
        return self.properties.get("manager", None)

    @property
    def mobile_phone(self):
        """
        The contact's mobile phone number.
        :rtype: str or None
        """
        return self.properties.get("mobilePhone", None)

    @mobile_phone.setter
    def mobile_phone(self, value):
        """
        Sets contact's mobile phone number.
        :type value: str
        """
        self.set_property("mobilePhone", value)

    @property
    def extensions(self):
        """The collection of open extensions defined for the contact. Nullable."""
        return self.properties.get('extensions',
                                   ExtensionCollection(self.context, ResourcePath("extensions", self.resource_path)))
