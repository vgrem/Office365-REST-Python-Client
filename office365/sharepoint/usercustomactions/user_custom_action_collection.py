from office365.runtime.client_object_collection import ClientObjectCollection
from office365.sharepoint.usercustomactions.user_custom_action import UserCustomAction


class UserCustomActionCollection(ClientObjectCollection):

    def __init__(self, context, resource_path=None):
        super(UserCustomActionCollection, self).__init__(context, UserCustomAction, resource_path)
