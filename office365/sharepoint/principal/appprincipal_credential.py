from office365.runtime.queries.service_operation import ServiceOperationQuery
from office365.sharepoint.base_entity import BaseEntity


class AppPrincipalCredential(BaseEntity):
    """Represents a credential belonging to an app principal."""

    @staticmethod
    def create_from_key_group(context, key_group_identifier):
        """
        Create an instance of SP.AppPrincipalCredential that wraps a key group identifier.

        :type context: office365.sharepoint.client_context.ClientContext
        :param str key_group_identifier:  The key group identifier.
        """
        return_type = AppPrincipalCredential(context)
        payload = {"keyGroupIdentifier": key_group_identifier}
        qry = ServiceOperationQuery(return_type, "CreateFromKeyGroup", None, payload, None, return_type)
        qry.static = True
        context.add_query(qry)
        return return_type
