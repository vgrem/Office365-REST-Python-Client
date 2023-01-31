from office365.runtime.client_result import ClientResult
from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.directory.my_groups_result import MyGroupsResult


class User(BaseEntity):

    def is_member_of(self, group_id):
        result = ClientResult(self.context)

        def _user_loaded():
            from office365.sharepoint.directory.SPHelper import SPHelper
            SPHelper.is_member_of(self.context, self.properties["principalName"], group_id, result)

        self.ensure_property('principalName', _user_loaded)
        return result

    def get_my_groups(self):
        return_type = MyGroupsResult(self.context)

        def _user_loaded():
            from office365.sharepoint.directory.SPHelper import SPHelper
            SPHelper.get_my_groups(self.context, self.properties["principalName"], 0, 10, return_type)
        self.ensure_property('principalName', _user_loaded)
        return return_type
