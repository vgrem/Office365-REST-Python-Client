from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class DocumentId(BaseEntity):
    """
    Contains methods that enable or disable the capability to assign Document IDs to query Document ID feature
    and assignment status, and to query and set Document ID providers.

    Provides methods for assigning Document Ids to documents, and provides methods to use lookup and search
    to get documents by their Document ID.
    """

    def __init__(self, context):
        super(DocumentId, self).__init__(context, ResourcePath("SP.DocumentManagement.DocumentId"))

    def reset_docid_by_server_relative_path(self, decoded_url):
        """In case the document identifier assigned by the document id feature is not unique, MUST re-assign
        the identifier and URL to ensure they are globally unique in the farm.

        :param str decoded_url: server relative path to the specified document for which the document identifier
             MUST be reset if it is not unique.
        """
        payload = {"DecodedUrl": decoded_url}
        qry = ServiceOperationQuery(self, "ResetDocIdByServerRelativePath", None, payload, None, None)
        self.context.add_query(qry)
        return self

    def reset_docids_in_library(self, decoded_url, content_type_id):
        """
        Performs the same function as ResetDocIdByServerRelativePath (section 3.1.5.10.2.1.1), but for every
        document in the specified document library.

        :param str decoded_url: Server relative path to the document library, for which all document identifiers MUST be reset to guarantee
            global uniqueness in the farm.
        :param str content_type_id: The content type identifier.
        """
        payload = {"DecodedUrl": decoded_url, "contentTypeId": content_type_id}
        qry = ServiceOperationQuery(self, "ResetDocIdsInLibrary", None, payload, None, None)
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "SP.DocumentManagement.DocumentId"
