from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class WebApplication(BaseEntity):

    @staticmethod
    def lookup(context, request_uri):
        """
        :type context
        :type request_uri str
        """
        return_type = WebApplication(context)
        payload = {"requestUri": request_uri}
        qry = ServiceOperationQuery(return_type, "Lookup", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Administration.SPWebApplication"
