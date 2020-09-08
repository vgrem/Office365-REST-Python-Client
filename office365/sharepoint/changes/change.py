from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.change_token import ChangeToken


class Change(BaseEntity):

    @staticmethod
    def resolve_change_type(type_id):
        mapping_types = {
        }
        return mapping_types.get(type_id, Change)

    @property
    def change_token(self):
        """
        Returns an ChangeToken that represents the change.
        """
        return self.properties.get("ChangeToken", ChangeToken())

    @property
    def change_type(self):
        """
        Returns an SPChangeType that indicates the type of change, including adding, updating, deleting, or renaming
        changes, but also moving items away from or into lists and folders.
        """
        return self.properties.get("ChangeType", None)

    @property
    def site_id(self):
        """
        Returns the Id of the site of the changed item
        """
        return self.properties.get("SiteId", None)

    def set_property(self, name, value, persist_changes=True):
        super(Change, self).set_property(name, value, persist_changes)
        #if name == "ChangeType":
        #    self.__class__ = self.resolve_change_type(value)
        return self
