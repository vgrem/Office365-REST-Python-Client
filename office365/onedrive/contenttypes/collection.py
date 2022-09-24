from office365.entity_collection import EntityCollection
from office365.onedrive.contenttypes.content_type import ContentType
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


class ContentTypeCollection(EntityCollection):

    def __init__(self, context, resource_path):
        super(ContentTypeCollection, self).__init__(context, ContentType, resource_path)

    def add_copy(self, content_type):
        """
        Add a copy of a content type from a site to a list.

        :param str content_type: Canonical URL to the site content type that will be copied to the list.
        """
        payload = {
            "contentType": content_type
        }
        return_type = ContentType(self.context)
        qry = ServiceOperationQuery(self, "addCopy", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add_copy_from_content_type_hub(self, content_type_id):
        """
        his method is part of the content type publishing changes to optimize the syncing of published content types
        to sites and lists, effectively switching from a "push everywhere" to "pull as needed" approach.
        The method allows users to pull content types directly from the content type hub to a site or list.

        :param str content_type_id: The ID of the content type in the content type hub that will be added to a target
            site or a list.
        """
        payload = {
            "contentTypeId": content_type_id
        }
        return_type = ContentType(self.context)
        qry = ServiceOperationQuery(self, "addCopyFromContentTypeHub", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def get_compatible_hub_content_types(self):
        """
        Get a list of compatible content types from the content type hub that can be added to a target site or a list.

        This method is part of the content type publishing changes to optimize the syncing of published content types
        to sites and lists, effectively switching from a "push everywhere" to "pull as needed" approach.
        The method allows users to pull content types directly from the content type hub to a site or list.
        """
        def _construct_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.method = HttpMethod.Get

        return_type = ContentTypeCollection(self.context, self.resource_path)
        qry = ServiceOperationQuery(self, "getCompatibleHubContentTypes", None, None, None, return_type)
        self.context.add_query(qry)
        self.context.before_execute(_construct_request)
        return return_type
