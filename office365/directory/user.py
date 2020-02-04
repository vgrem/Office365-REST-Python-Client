from office365.directory.directoryObject import DirectoryObject
from office365.onedrive.drive import Drive
from office365.outlookservices.contact_collection import ContactCollection
from office365.outlookservices.event_collection import EventCollection
from office365.outlookservices.message_collection import MessageCollection
from office365.runtime.client_query import ClientQuery
from office365.runtime.resource_path_entity import ResourcePathEntity
from office365.runtime.utilities.http_method import HttpMethod


class User(DirectoryObject):
    """Represents an Azure AD user account. Inherits from directoryObject."""

    @property
    def drive(self):
        """Retrieve the properties and relationships of a Drive resource."""
        if self.is_property_available('drive'):
            return self.properties['drive']
        else:
            return Drive(self.context, ResourcePathEntity(self.context, self.resourcePath, "drive"))

    @property
    def contacts(self):
        """Get a contact collection from the default Contacts folder of the signed-in user (.../me/contacts),
        or from the specified contact folder."""
        if self.is_property_available('contacts'):
            return self.properties['contacts']
        else:
            return ContactCollection(self.context, ResourcePathEntity(self, self.resourcePath, "contacts"))

    @property
    def events(self):
        """Get an event collection or an event."""
        if self.is_property_available('events'):
            return self.properties['events']
        else:
            return EventCollection(self.context, ResourcePathEntity(self, self.resourcePath, "events"))

    @property
    def messages(self):
        """Get an event collection or an event."""
        if self.is_property_available('messages'):
            return self.properties['messages']
        else:
            return MessageCollection(self.context, ResourcePathEntity(self, self.resourcePath, "messages"))

    def send_mail(self, message):
        """Send a new message on the fly"""
        url = self.resourceUrl + "/sendmail"
        qry = ClientQuery(url, HttpMethod.Post, message)
        self.context.add_query(qry)
