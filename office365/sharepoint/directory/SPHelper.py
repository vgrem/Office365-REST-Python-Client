from office365.runtime.paths.resource_path import ResourcePath
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.directory.user import User


class SPHelper(BaseEntity):

    def __init__(self, context):
        super(SPHelper, self).__init__(context, ResourcePath("SP.Directory.SPHelper"))

    @staticmethod
    def get_members(context, group_id, return_type=None):
        """
        :param str group_id: Group identifier
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context
        :param BaseEntityCollection or None return_type: Returns members
        """
        if return_type is None:
            return_type = BaseEntityCollection(context, User)
        helper = SPHelper(context)
        qry = ServiceOperationQuery(helper, "GetMembers", [group_id], None, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "SP.Directory.SPHelper"
