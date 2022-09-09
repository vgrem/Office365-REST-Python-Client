import random

from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class GroupService(BaseEntity):

    def __init__(self, context, resource_path=None):
        super(GroupService, self).__init__(context, resource_path)

    def get_group_image(self, group_id, image_hash=None, image_color=None):
        """
        :param str group_id:
        :param int or None image_hash:
        :param str or None image_color:
        """
        return_type = ClientResult(self.context)
        if image_hash is None:
            image_hash = random.getrandbits(64)
        qry = ServiceOperationQuery(self, "GetGroupImage", None, None, None, return_type)

        def _modify_request(request):
            """
            :type request: office365.runtime.http.request_options.RequestOptions
            """
            request.url += "?id='{0}'&hash={1}".format(group_id, image_hash)
            request.method = HttpMethod.Get
        self.context.before_execute(_modify_request)
        self.context.add_query(qry)
        return return_type

    def sync_group_properties(self):
        qry = ServiceOperationQuery(self, "SyncGroupProperties")
        self.context.add_query(qry)
        return self

    @property
    def entity_type_name(self):
        return "Microsoft.SharePoint.Portal.GroupService"
