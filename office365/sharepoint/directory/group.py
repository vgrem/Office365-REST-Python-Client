from office365.sharepoint.directory.helper import SPHelper
from office365.sharepoint.directory.members_info import MembersInfo
from office365.sharepoint.entity import Entity
from office365.sharepoint.entity_collection import EntityCollection


class Group(Entity):
    def get_members_info(self, row_limit):
        """"""
        result = MembersInfo(self.context)

        def _user_loaded():
            from office365.sharepoint.directory.helper import SPHelper

            SPHelper.get_members_info(
                self.context, self.properties["Id"], row_limit, result
            )

        self.ensure_property("Id", _user_loaded)
        return result

    def get_members(self):
        """"""
        from office365.directory.users.user import User

        members = EntityCollection(self.context, User)

        def _group_loaded():
            SPHelper.get_members(self.context, self.properties["Id"], members)

        self.ensure_property("Id", _group_loaded)
        return members

    def get_owners(self):
        """"""
        from office365.directory.users.user import User

        owners = EntityCollection(self.context, User)

        def _group_loaded():
            SPHelper.get_owners(self.context, self.properties["Id"], owners)

        self.ensure_property("Id", _group_loaded)
        return owners

    @property
    def entity_type_name(self):
        return "SP.Directory.Group"
