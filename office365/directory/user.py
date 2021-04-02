from office365.calendar.calendar import Calendar
from office365.calendar.calendar_collection import CalendarCollection
from office365.calendar.calendar_group_collection import CalendarGroupCollection
from office365.directory.directoryObject import DirectoryObject
from office365.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.directory.objectIdentity import ObjectIdentity
from office365.directory.profilePhoto import ProfilePhoto
from office365.onedrive.drive import Drive
from office365.mail.contact_collection import ContactCollection
from office365.calendar.event_collection import EventCollection
from office365.mail.message_collection import MessageCollection
from office365.runtime.client_value_collection import ClientValueCollection
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath
from office365.teams.team_collection import TeamCollection


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    def send_mail(self, message):
        """Send a new message on the fly"""
        qry = ServiceOperationQuery(self, "sendmail", None, message)
        self.context.add_query(qry)
        return self

    def delete_object(self, permanent_delete=False):
        """
        :param permanent_delete: Permanently deletes the user from directory
        :type permanent_delete: bool

        """
        super(User, self).delete_object()
        if permanent_delete:
            deleted_user = self.context.directory.deletedUsers[self.id]
            deleted_user.delete_object()
        return self

    @property
    def creationType(self):
        """Indicates whether the user account was created as a regular school or work account (null),
        an external account (Invitation), a local account for an Azure Active Directory B2C tenant (LocalAccount)
        or self-service sign-up using email verification (EmailVerified). Read-only.
        """
        return self.properties.get('creationType', None)

    @property
    def mail(self):
        """The SMTP address for the user, for example, "jeff@contoso.onmicrosoft.com".
           Returned by default. Supports $filter and endsWith.
        """
        return self.properties.get('mail', None)

    @property
    def otherMails(self):
        """A list of additional email addresses for the user;
        for example: ["bob@contoso.com", "Robert@fabrikam.com"]. Supports $filter.
        """
        return self.properties.get('otherMails', ClientValueCollection(str))

    @property
    def identities(self):
        """Represents the identities that can be used to sign in to this user account.
           An identity can be provided by Microsoft (also known as a local account), by organizations,
           or by social identity providers such as Facebook, Google, and Microsoft, and tied to a user account.
           May contain multiple items with the same signInType value.
           Supports $filter.
        """
        return self.properties.get('identities',
                                   ClientValueCollection(ObjectIdentity))

    @property
    def photo(self):
        """
        The user's profile photo. Read-only.
        """
        return self.properties.get('photo',
                                   ProfilePhoto(self.context, ResourcePath("photo", self.resource_path)))

    @property
    def manager(self):
        """
        The user or contact that is this user's manager. Read-only. (HTTP Methods: GET, PUT, DELETE.)
        """
        return self.properties.get('manager',
                                   DirectoryObject(self.context, ResourcePath("manager", self.resource_path)))

    @property
    def calendar(self):
        """The user's primary calendar. Read-only."""
        return self.properties.get('calendar',
                                   Calendar(self.context, ResourcePath("calendar", self.resource_path)))

    @property
    def calendars(self):
        """The user's calendar groups. Read-only. Nullable."""
        return self.properties.get('calendars',
                                   CalendarCollection(self.context, ResourcePath("calendars", self.resource_path)))

    @property
    def calendarGroups(self):
        """The user's calendar groups. Read-only. Nullable."""
        return self.properties.get('calendarGroups',
                                   CalendarGroupCollection(self.context,
                                                           ResourcePath("calendarGroups", self.resource_path)))

    @property
    def drive(self):
        """Retrieve the properties and relationships of a Drive resource."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            return Drive(self.context, ResourcePath("drive", self.resource_path))

    @property
    def contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        if self.is_property_available('contacts'):
            return self.properties['contacts']
        else:
            return ContactCollection(self.context, ResourcePath("contacts", self.resource_path))

    @property
    def events(self):
        """Get an event collection or an event."""
        if self.is_property_available('events'):
            return self.properties['events']
        else:
            return EventCollection(self.context, ResourcePath("events", self.resource_path))

    @property
    def messages(self):
        """Get an event collection or an event."""
        if self.is_property_available('messages'):
            return self.properties['messages']
        else:
            return MessageCollection(self.context, ResourcePath("messages", self.resource_path))

    @property
    def joinedTeams(self):
        """Get the teams in Microsoft Teams that the user is a direct member of."""
        return self.properties.get('joinedTeams',
                                   TeamCollection(self.context, ResourcePath("joinedTeams", self.resource_path)))

    @property
    def memberOf(self):
        """Get groups and directory roles that the user is a direct member of."""
        return self.properties.get('memberOf',
                                   DirectoryObjectCollection(self.context,
                                                             ResourcePath("memberOf", self.resource_path)))

    @property
    def transitiveMemberOf(self):
        """Get groups, directory roles that the user is a member of. This API request is transitive, and will also
        return all groups the user is a nested member of. """
        if self.is_property_available('transitiveMemberOf'):
            return self.properties['transitiveMemberOf']
        else:
            return DirectoryObjectCollection(self.context, ResourcePath("transitiveMemberOf", self.resource_path))

    def set_property(self, name, value, persist_changes=True):
        super(User, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "id" or name == "userPrincipalName":
                self._resource_path = ResourcePath(
                    value,
                    self._parent_collection.resource_path)
        return self
