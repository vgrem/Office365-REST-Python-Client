from office365.graph.directory.directoryObject import DirectoryObject
from office365.graph.directory.directoryObjectCollection import DirectoryObjectCollection
from office365.graph.directory.groupCollection import GroupCollection
from office365.graph.onedrive.drive import Drive
from office365.outlookservices.contact_collection import ContactCollection
from office365.outlookservices.event_collection import EventCollection
from office365.outlookservices.messageCollection import MessageCollection
from office365.runtime.resource_path import ResourcePath
from office365.runtime.serviceOperationQuery import ServiceOperationQuery


def _delete_user_from_directory(target_user):
    """
    Deletes the user from directory

    :type target_user: User
    """
    deleted_user = target_user.context.directory.deletedUsers[target_user.id]
    deleted_user.delete_object()


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    def delete_object(self, permanent_delete=False):
        """
        :param permanent_delete: Permanently deletes the user from directory
        :type permanent_delete: bool

        """
        super(User, self).delete_object()
        if permanent_delete:
            self.ensure_property("id", _delete_user_from_directory)

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

    def send_mail(self, message):
        """Send a new message on the fly"""
        qry = ServiceOperationQuery(self, "sendmail", None, message)
        self.context.add_query(qry)

    @property
    def joinedTeams(self):
        """Get the teams in Microsoft Teams that the user is a direct member of."""
        if self.is_property_available('joinedTeams'):
            return self.properties['joinedTeams']
        else:
            return GroupCollection(self.context, ResourcePath("joinedTeams", self.resource_path))

    @property
    def memberOf(self):
        """Get groups and directory roles that the user is a direct member of."""
        if self.is_property_available('memberOf'):
            return self.properties['memberOf']
        else:
            return DirectoryObjectCollection(self.context, ResourcePath("memberOf", self.resource_path))

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
