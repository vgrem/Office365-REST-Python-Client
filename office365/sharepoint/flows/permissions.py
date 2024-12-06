from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.entity import Entity


class FlowPermissions(Entity):

    @staticmethod
    def get_flow_permission_level_on_list(context, list_name):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint client context
         :param str list_name: Specifies the list name.
        """
        return_type = ClientResult(context)
        payload = {"listName": list_name}
        qry = ServiceOperationQuery(
            FlowPermissions(context),
            "GetFlowPermissionLevelOnList",
            None,
            payload,
            None,
            return_type,
            True,
        )
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Internal.FlowPermissions"
