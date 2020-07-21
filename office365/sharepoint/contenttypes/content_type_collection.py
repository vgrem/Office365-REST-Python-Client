from office365.runtime.client_object_collection import ClientObjectCollection
from office365.runtime.client_query import CreateEntityQuery
from office365.runtime.resource_path_service_operation import ResourcePathServiceOperation
from office365.sharepoint.contenttypes.content_type import ContentType


class ContentTypeCollection(ClientObjectCollection):
    """Content Type resource collection"""

    def __init__(self, context, resource_path=None):
        super(ContentTypeCollection, self).__init__(context, ContentType, resource_path)

    def get_by_id(self, contentTypeId):
        """
        Returns the content type with the given identifier from the collection.
        If a content type with the given identifier is not found in the collection, the server MUST return null.

        :param str contentTypeId: A hexadecimal value representing the identifier of a content type.
        """
        return ContentType(self.context, ResourcePathServiceOperation("GetById", [contentTypeId], self.resource_path))

    def add(self, contentTypeInfo):
        """Adds a new content type to the collection and returns a reference to the added SP.ContentType.

        :param ContentTypeCreationInformation contentTypeInfo: Specifies properties that is to be used to construct
           the new content type.

        """
        ct = ContentType(self.context)
        self.add_child(ct)
        ct_json = contentTypeInfo.to_json()
        for k, v in ct_json.items():
            if k == "Id":
                ct.set_property(k, {"StringValue": v}, True)
            else:
                ct.set_property(k, v, True)
        qry = CreateEntityQuery(self, ct, ct)
        self.context.add_query(qry)
        return ct

    def add_available_content_type(self, contentTypeId):
        """Adds the specified content type to the content type collection.

        :param str contentTypeId: Specifies the identifier of the content type to be added to the content type
            collection. It MUST exist in the web's available content types.

        """
        pass

    def add_existing_content_type(self, contentType):
        """Adds an existing content type to the collection. The name of the given content type MUST NOT be the same
        as any of the content types in the collection. A reference to the SP.ContentType that was added is returned.

        :param ContentType contentType: Specifies the content type to be added to the collection

        """
        pass
