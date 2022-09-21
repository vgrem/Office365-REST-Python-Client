from office365.runtime.client_value_collection import ClientValueCollection
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.userprofiles.sharedwithme.document_user import SharedWithMeDocumentUser


class SharedWithMeDocument(BaseEntity):
    """Represents a shared document."""

    @property
    def authors(self):
        """
        Specifies a list of users that authored the document.
        """
        return self.properties.get('Authors', ClientValueCollection(SharedWithMeDocumentUser))

    @property
    def caller_stack(self):
        return self.properties.get('CallerStack', None)

    @property
    def content_type_id(self):
        """
        Specifies the identifier of the content type of the document.
        """
        return self.properties.get('ContentTypeId', None)

    @property
    def doc_id(self):
        """
        Specifies the document identifier.
        """
        return self.properties.get('DocId', None)

    @property
    def editors(self):
        """
        Specifies a list of users that can edit the document.
        """
        return self.properties.get('Editors', ClientValueCollection(SharedWithMeDocumentUser))
