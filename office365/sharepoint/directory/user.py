from office365.runtime.client_result import ClientResult
from office365.sharepoint.base_entity import BaseEntity


class User(BaseEntity):

    def is_member_of(self, group_id):
        result = ClientResult(self.context)

        def _user_loaded():
            from office365.sharepoint.directory.SPHelper import SPHelper
            SPHelper.is_member_of(self.context, self.properties["principalName"], group_id, result)

        self.ensure_property('principalName', _user_loaded)
        return result

    def get_my_groups(self):
        result = ClientResult(self.context)

        def _user_loaded():
            from office365.sharepoint.directory.SPHelper import SPHelper
            SPHelper.get_my_groups(self.context, self.properties["principalName"], 0, 10, result)
        self.ensure_property('principalName', _user_loaded)
        return result
