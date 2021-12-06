from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.base_entity_collection import BaseEntityCollection
from office365.sharepoint.directory.SPHelper import SPHelper


class Group(BaseEntity):

    def get_members(self):
        from office365.directory.users.user import User
        members = BaseEntityCollection(self.context, User)

        def _group_loaded():
            SPHelper.get_members(self.context, self.properties["Id"], members)
        self.ensure_property("Id", _group_loaded)
        return members
