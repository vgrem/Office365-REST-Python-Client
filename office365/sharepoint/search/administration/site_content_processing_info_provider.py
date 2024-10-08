from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class SiteContentProcessingInfoProvider(Entity):

    def get_azure_container_token(self):
        return_type = ClientResult(self.context, str())
        qry = ServiceOperationQuery(
            self, "GetAzureContainerToken", None, None, None, return_type
        )
        self.context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Client.Search.Administration.SiteContentProcessingInfoProvider"
