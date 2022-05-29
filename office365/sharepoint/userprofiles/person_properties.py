from office365.runtime.types.string_collection import StringCollection
from office365.sharepoint.base_entity import BaseEntity


class PersonProperties(BaseEntity):
    """
    The PersonProperties class contains the data about people and is returned by PeopleManager methods
    (see section 3.1.5.58).
    """

    @property
    def extended_managers(self):
        """
        The ExtendedManagers property specifies an array of strings that specify the account names of
        a person's managers.

        :rtype: StringCollection
        """
        return self.properties.get('ExtendedManagers', StringCollection())

    @property
    def extended_reports(self):
        """
        The ExtendedReports properties specifies an array of strings that specify the account names of
        person's extended reports.

        :rtype: StringCollection
        """
        return self.properties.get('ExtendedReports', StringCollection())

    @property
    def user_url(self):
        """
        The UserUrl property specifies the URL for the person's profile.

        :rtype: str or None
        """
        return self.properties.get('UserUrl', None)

    def get_property(self, name, default_value=None):
        if default_value is None:
            property_mapping = {
                "ExtendedManagers": self.extended_managers,
                "ExtendedReports": self.extended_reports
            }
            default_value = property_mapping.get(name, None)
        return super(PersonProperties, self).get_property(name, default_value)
