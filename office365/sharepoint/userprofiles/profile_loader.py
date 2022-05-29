from office365.runtime.client_object import ClientObject
from office365.runtime.queries.service_operation_query import ServiceOperationQuery
from office365.runtime.paths.resource_path import ResourcePath
from office365.sharepoint.userprofiles.userProfile import UserProfile


class ProfileLoader(ClientObject):

    def __init__(self, context):
        super(ProfileLoader, self).__init__(context, ResourcePath("SP.UserProfiles.ProfileLoader.GetProfileLoader"))

    @staticmethod
    def get_profile_loader(context):
        """
        :type: office365.sharepoint.client_context.ClientContext context
        """
        result = ProfileLoader(context)
        qry = ServiceOperationQuery(result, "GetProfileLoader", None, None, None, result)
        qry.static = True
        context.add_query(qry)
        return result

    def get_user_profile(self):
        result = UserProfile(self.context, ResourcePath("GetUserProfile", self.resource_path))
        qry = ServiceOperationQuery(self, "GetUserProfile", None, None, None, result)
        self.context.add_query(qry)
        return result

    @property
    def entity_type_name(self):
        return "SP.UserProfiles.ProfileLoader"
