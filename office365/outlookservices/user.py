from office365.outlookservices.contact_collection import ContactCollection
from office365.outlookservices.event_collection import EventCollection
from office365.outlookservices.message_collection import MessageCollection
from office365.runtime.client_object import ClientObject
from office365.runtime.resource_path_entry import ResourcePathEntry


class User(ClientObject):
    """A user in the system."""

    @property
    def contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        contacts = ContactCollection(self.context, ResourcePathEntry(self, self._resource_path, "contacts"))
        return contacts

    @property
    def events(self):
        """Get an event collection or an event."""
        events = EventCollection(self.context, ResourcePathEntry(self, self._resource_path, "events"))
        return events

    @property
    def messages(self):
        """Get an event collection or an event."""
        messages = MessageCollection(self.context, ResourcePathEntry(self, self._resource_path, "messages"))
        return messages
