from office365.runtime.queries.create_entity_query import CreateEntityQuery
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.service_operation import ServiceOperationPath
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.contenttypes.content_type import ContentType


class ContentTypeCollection(BaseEntityCollection):
    """Content Type resource collection"""

    def __init__(self, context, resource_path=None, parent=None):
        super(ContentTypeCollection, self).__init__(context, ContentType, resource_path, parent)

    def get_by_id(self, contentTypeId):
        """
        Returns the content type with the given identifier from the collection.
        If a content type with the given identifier is not found in the collection, the server MUST return null.

        :param str contentTypeId: A hexadecimal value representing the identifier of a content type.
        """
        return ContentType(self.context, ServiceOperationPath("GetById", [contentTypeId], self.resource_path))

    def add(self, content_type_info):
        """Adds a new content type to the collection and returns a reference to the added SP.ContentType.

        :param ContentTypeCreationInformation content_type_info: Specifies properties that is to be used to
            construct the new content type.

        """
        ct = ContentType(self.context)
        self.add_child(ct)
        ct_json = content_type_info.to_json()
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
        ct = ContentType(self.context)
        self.add_child(ct)
        qry = ServiceOperationQuery(self, "AddAvailableContentType", [contentTypeId], None, None, ct)
        self.context.add_query(qry)
        return ct

    def add_existing_content_type(self, content_type):
        """Adds an existing content type to the collection. The name of the given content type MUST NOT be the same
        as any of the content types in the collection. A reference to the SP.ContentType that was added is returned.

        :param ContentType content_type: Specifies the content type to be added to the collection

        """
        pass
