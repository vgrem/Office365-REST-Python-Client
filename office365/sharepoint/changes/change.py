from office365.sharepoint.base_entity import BaseEntity
from office365.sharepoint.changes.token import ChangeToken


class Change(BaseEntity):

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

    @property
    def time(self):
        """
        Gets a value that specifies the time that the object was modified.
        """
        return self.properties.get("Time", None)
