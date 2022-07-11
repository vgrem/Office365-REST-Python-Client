from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.administration.web_application import WebApplication
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection


class SPWebService(BaseEntity):

    @staticmethod
    def content_service(context):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        """
        return_type = SPWebService(context)
        qry = ServiceOperationQuery(return_type, "ContentService", None, None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def web_applications(self):
        return self.properties.get('WebApplications',
                                   BaseEntityCollection(self.context, WebApplication,
                                                        ResourcePath("WebApplications", self.resource_path)))

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.SPWebService"
