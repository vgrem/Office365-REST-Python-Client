from office365.delta_collection import DeltaCollection
from office365.directory.object import DirectoryObject
from office365.entity_collection import EntityCollection
from office365.runtime.client_result import ClientResult
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.queries.service_operation import ServiceOperationQuery


class DirectoryObjectCollection(DeltaCollection):
    """DirectoryObject's collection"""

    def __init__(self, context, resource_path=None):
        super(DirectoryObjectCollection, self).__init__(context, DirectoryObject, resource_path)

    def get_by_ids(self, ids):
        """
        Returns the directory objects specified in a list of IDs.

        :type ids: list[str]
        """
        return_type = ClientResult(self.context)
        params = {
            "ids": ids
        }
        qry = ServiceOperationQuery(self, "getByIds", params, None, None, return_type)
        self.context.add_query(qry)
        return return_type

    def add(self, user_id):
        """
        Add a user to the group.

        :type user_id: str
        """
        payload = {
            "@odata.id": "https://graph.microsoft.com/v1.0/users/{0}".format(user_id)
        }
        qry = ServiceOperationQuery(self, "$ref", None, payload)
        self.context.add_query(qry)
        return self

    def get_available_extension_properties(self, is_synced_from_on_premises=None):
        """
        Return all or a filtered list of the directory extension properties that have been registered in a directory.
        The following entities support extension properties: user, group, organization, device, application,
        and servicePrincipal.
        """
        from office365.directory.extensions.extension_property import ExtensionProperty
        return_type = EntityCollection(self.context, ExtensionProperty, self.context.directory_objects.resource_path)
        payload = {
            "isSyncedFromOnPremises": is_synced_from_on_premises
        }
        qry = ServiceOperationQuery(self, "getAvailableExtensionProperties", None, payload, None, return_type)
        self.context.add_query(qry)
        return return_type

    def remove(self, user_id):
        """Remove a user from the group.

        :param str user_id: User identifier
        """

        qry = ServiceOperationQuery(self, "{0}/$ref".format(user_id))

        def _construct_request(request):
            """
            :type request: RequestOptions
            """
            request.method = HttpMethod.Delete
        self.context.add_query(qry).before_query_execute(_construct_request)
        return self

    def validate_properties(self, entity_type=None, display_name=None, mail_nickname=None, on_behalf_of_userid=None):
        """
        Validate that a Microsoft 365 group's display name or mail nickname complies with naming policies.
        Clients can use this API to determine whether a display name or mail nickname is valid before trying to
        create a Microsoft 365 group. To validate the properties of an existing group, use the group:
        validateProperties function.

        :param str entity_type: Group is the only supported entity type.
        :param str display_name: The display name of the group to validate. The property is not individually required.
             However, at least one property (displayName or mailNickname) is required.
        :param str mail_nickname: The mail nickname of the group to validate.
             The property is not individually required. However, at least one property (displayName or mailNickname)
             is required.
        :param str on_behalf_of_userid: The ID of the user to impersonate when calling the API. The validation results
            are for the onBehalfOfUserId's attributes and roles.
        """
        payload = {
            "entityType": entity_type,
            "displayName": display_name,
            "mailNickname": mail_nickname,
            "onBehalfOfUserId": on_behalf_of_userid
        }
        qry = ServiceOperationQuery(self, "validateProperties", None, payload)
        self.context.add_query(qry)
        return self
