from office365.runtime.client_result import ClientResult
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class Reputation(BaseEntity):

    @staticmethod
    def set_rating(context, list_id, item_id, rating, return_type=None):
        """
        :param office365.sharepoint.client_context.ClientContext context: SharePoint context (client)
        :param str list_id: List Identifier
        :param int item_id: ListItem Identifier
        :param int rating: Rating number
        :param ClientResult return_type: return value
        """
        if return_type is None:
            return_type = ClientResult(context)

        binding_type = Reputation(context)
        payload = {
            "listID": list_id,
            "itemID": item_id,
            "rating": rating
        }
        qry = ServiceOperationQuery(binding_type, "SetRating", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @staticmethod
    def set_like(context, list_id, item_id, like, return_type=None):
        """
        :param office365.sharepoint.client_context.ClientContext context:
        :param str list_id: List Identifier
        :param int item_id: ListItem Identifier
        :param bool like: Like/Dislike value
        :param ClientResult return_type: return value
        """
        if return_type is None:
            return_type = ClientResult(context)
        binding_type = Reputation(context)
        payload = {
            "listID": list_id,
            "itemID": item_id,
            "like": like
        }
        qry = ServiceOperationQuery(binding_type, "SetLike", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type

    @property
    def entity_type_name(self):
        return "Microsoft.Office.Server.ReputationModel.Reputation"

