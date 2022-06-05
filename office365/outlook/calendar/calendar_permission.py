from office365.entity import Entity
from office365.outlook.calendar.email_address import EmailAddress


class CalendarPermission(Entity):
    """
    The permissions of a user with whom the calendar has been shared or delegated in an Outlook client.

    Get, update, and delete of calendar permissions is supported on behalf of only the calendar owner.

    Getting the calendar permissions of a calendar on behalf of a sharee or delegate returns
    an empty calendar permissions collection.

    Once a sharee or delegate has been set up for a calendar, you can update only the role property to change
    the permissions of a sharee or delegate. You cannot update the allowedRoles, emailAddress, isInsideOrganization,
    or isRemovable property. To change these properties, you should delete the corresponding calendarPermission
    object and create another sharee or delegate in an Outlook client.

    """

    @property
    def email_address(self):
        """
        Represents a sharee or delegate who has access to the calendar.
        For the "My Organization" sharee, the address property is null. Read-only.
        """
        return self.properties.get("emailAddress", EmailAddress())

    @property
    def is_removable(self):
        """
        True if the user can be removed from the list of sharees or delegates for the specified calendar,
        false otherwise. The "My organization" user determines the permissions other people within your organization
        have to the given calendar. You cannot remove "My organization" as a sharee to a calendar.

        :rtype: bool or None
        """
        return self.properties.get("isRemovable", None)
