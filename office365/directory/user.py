from office365.directory.directoryObject import DirectoryObject
from office365.onedrive.drive import Drive
from office365.outlookservices.contact_collection import ContactCollection
from office365.outlookservices.event_collection import EventCollection
from office365.outlookservices.messageCollection import MessageCollection
from office365.runtime.client_query import ServiceOperationQuery
from office365.runtime.resource_path import ResourcePath


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    @property
    def drive(self):
        """Retrieve the properties and relationships of a Drive resource."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            return Drive(self.context, ResourcePath("drive", self.resourcePath))

    @property
    def contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        if self.is_property_available('contacts'):
            return self.properties['contacts']
        else:
            return ContactCollection(self.context, ResourcePath("contacts", self.resourcePath))

    @property
    def events(self):
        """Get an event collection or an event."""
        if self.is_property_available('events'):
            return self.properties['events']
        else:
            return EventCollection(self.context, ResourcePath("events", self.resourcePath))

    @property
    def messages(self):
        """Get an event collection or an event."""
        if self.is_property_available('messages'):
            return self.properties['messages']
        else:
            return MessageCollection(self.context, ResourcePath("messages", self.resourcePath))

    def send_mail(self, message):
        """Send a new message on the fly"""
        qry = ServiceOperationQuery(self, "sendmail", None, message)
        self.context.add_query(qry)

    def set_property(self, name, value, persist_changes=True):
        super(User, self).set_property(name, value, persist_changes)
        # fallback: create a new resource path
        if self._resource_path is None:
            if name == "id" or name == "userPrincipalName":
                self._resource_path = ResourcePath(
                    value,
                    self._parent_collection.resourcePath)
