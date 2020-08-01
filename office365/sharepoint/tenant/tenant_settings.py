from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class TenantSettings(BaseEntity):

    @staticmethod
    def current(context):
        """

        :type context: ClientContext
        :return: TenantSettings
        """
        settings = TenantSettings(context)
        qry = ServiceOperationQuery(settings, "Current", None, None, None, settings)
        qry.static = True
        context.add_query(qry)
        return settings
