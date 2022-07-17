from office365.directory.extensions.extended_property import SingleValueLegacyExtendedProperty, \
    MultiValueLegacyExtendedProperty
from office365.directory.extensions.extension import Extension
from office365.directory.profile_photo import ProfilePhoto
from office365.entity_collection import EntityCollection
from office365.outlook.calendar.email_address import EmailAddress
from office365.outlook.item import OutlookItem
from office365.outlook.mail.physical_address import PhysicalAddress
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.paths.resource_path import ResourcePath


class Contact(OutlookItem):
    """User's contact."""

    @property
    def manager(self):
        """
        The name of the contact's manager.

        :rtype: str or None
        """
        return self.properties.get("manager", None)

    @manager.setter
    def manager(self, value):
        """
        Sets name of the contact's manager.

        :type value: str
        """
        self.set_property("manager", value)

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
    def home_address(self):
        return self.properties.get("homeAddress", PhysicalAddress())

    @property
    def email_addresses(self):
        """The contact's email addresses."""
        return self.properties.get("emailAddresses", ClientValueCollection(EmailAddress))

    @email_addresses.setter
    def email_addresses(self, value):
        """Sets contact's email addresses.

        :type value: list[str]
        """
        self.set_property("emailAddresses", value)

    @property
    def extensions(self):
        """The collection of open extensions defined for the contact. Nullable."""
        return self.properties.get('extensions',
                                   EntityCollection(self.context, Extension,
                                                    ResourcePath("extensions", self.resource_path)))

    @property
    def photo(self):
        """Optional contact picture. You can get or set a photo for a contact."""
        return self.properties.get('photo',
                                   ProfilePhoto(self.context, ResourcePath("photo", self.resource_path)))

    @property
    def multi_value_extended_properties(self):
        """The collection of multi-value extended properties defined for the Contact."""
        return self.properties.get('multiValueExtendedProperties',
                                   EntityCollection(self.context, MultiValueLegacyExtendedProperty,
                                                    ResourcePath("multiValueExtendedProperties", self.resource_path)))

    @property
    def single_value_extended_properties(self):
        """The collection of single-value extended properties defined for the Contact."""
        return self.properties.get('singleValueExtendedProperties',
                                   EntityCollection(self.context, SingleValueLegacyExtendedProperty,
                                                    ResourcePath("singleValueExtendedProperties", self.resource_path)))

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "emailAddresses": self.email_addresses,
                "multiValueExtendedProperties": self.multi_value_extended_properties,
                "singleValueExtendedProperties": self.single_value_extended_properties
            }
            default_value = property_mapping.get(name, None)
        return super(Contact, self).get_property(name, default_value)
